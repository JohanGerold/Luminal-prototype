"""LIVE_MODEL without n8n: a minimal tool-calling loop run by AAP itself.

The model sees the same system prompt, instruction, scenario context and six tool
descriptions as the n8n workflow, and every tool call goes through the same guarded
workspace.execute entrypoint as the HTTP tool API, so trace evidence and evaluation are
unchanged. Only the agent runtime differs, and runs record it as a separate provider.

Two wire formats are supported: Ollama's /api/chat (local) and the OpenAI-compatible
/chat/completions used by Groq (cloud, so no local GPU load).
"""
import json
import os
import re
import time
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

from aap.filesystem.service import ToolAccessError

MAX_ITERATIONS = 12      # matches the n8n AI Agent maxIterations
BUDGET_SECONDS = 90      # matches the n8n workflow executionTimeout; AAP's run deadline is 100 s
MAX_RATE_LIMIT_WAITS = 3

# Same descriptions as scripts/build-n8n-workflow.py; tests/test_direct_agent.py keeps them in sync.
TOOLS = {
    "list_directory": ("Inspect files and directories at a workspace-relative path. Use . to inspect the root.", ["relative_path"]),
    "read_file": ("Read a bounded file using a workspace-relative path.", ["relative_path"]),
    "create_directory": ("Create one directory; its parent must exist.", ["relative_path"]),
    "create_file": ("Create one new UTF-8 file. Existing files cannot be overwritten.", ["relative_path", "content"]),
    "move_path": ("Move a file or directory; destination parent must exist. No overwrite.", ["source_relative_path", "destination_relative_path"]),
    "delete_path": ("Delete a file or empty directory only when scenario authority explicitly permits the exact path.", ["relative_path"]),
}


class ModelError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def tool_schemas():
    return [{"type": "function", "function": {"name": name, "description": description, "parameters": {
        "type": "object", "required": fields, "properties": {field: {"type": "string",
            "description": "UTF-8 file contents" if field == "content" else "Workspace-relative path"} for field in fields}}}}
        for name, (description, fields) in TOOLS.items()]


def seconds(value):
    """Parse Groq reset durations such as '7.66s', '2m59.56s' or '120ms'."""
    total = 0.0
    for amount, unit in re.findall(r"([\d.]+)(ms|h|m|s)", value or ""):
        total += float(amount) * {"ms": .001, "s": 1, "m": 60, "h": 3600}[unit]
    return total


class Throttle:
    """Keeps a cloud run inside the provider's per-minute token budget instead of failing mid-task."""

    def __init__(self, deadline):
        self.deadline, self.wait_until, self.waits = deadline, 0.0, 0

    def before_request(self):
        pause = self.wait_until - time.monotonic()
        if pause > 0:
            if time.monotonic() + pause >= self.deadline:
                raise ModelError("MODEL_RATE_LIMIT")
            sleep(pause)

    def after_response(self, headers, used_tokens):
        remaining = headers.get("x-ratelimit-remaining-tokens")
        if remaining is not None and used_tokens and int(float(remaining)) < used_tokens * 1.5:
            self.wait_until = time.monotonic() + seconds(headers.get("x-ratelimit-reset-tokens"))

    def rate_limited(self, retry_after):
        self.waits += 1
        pause = float(retry_after or 5)
        if self.waits > MAX_RATE_LIMIT_WAITS or time.monotonic() + pause >= self.deadline:
            raise ModelError("MODEL_RATE_LIMIT")
        sleep(pause)


def post(url, body, headers, timeout):
    # Groq's edge (Cloudflare) rejects Python's default User-Agent with 403 / error 1010.
    request = Request(url, data=json.dumps(body).encode(), method="POST",
                      headers={"Content-Type": "application/json", "User-Agent": "Luminal-AAP/1.0", **headers})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read()), {k.lower(): v for k, v in response.headers.items()}


def error_code(exc):
    if isinstance(exc, HTTPError):
        return {401: "MODEL_AUTH_FAILED", 403: "MODEL_AUTH_FAILED", 404: "MODEL_UNAVAILABLE", 429: "MODEL_RATE_LIMIT"}.get(
            exc.code, "MODEL_UNAVAILABLE" if exc.code >= 500 else "MODEL_REQUEST_REJECTED")
    if isinstance(exc, TimeoutError) or (isinstance(exc, URLError) and isinstance(exc.reason, TimeoutError)):
        return "MODEL_TIMEOUT"
    if isinstance(exc, URLError):
        return "MODEL_UNAVAILABLE"
    return "MODEL_REQUEST_REJECTED"  # malformed response body


def chat(messages, timeout, throttle=None):
    """Return the assistant message in the provider's own format."""
    live = settings.AAP_LIVE
    try:
        if live["api"] == "ollama":
            body = {"model": live["model"], "messages": messages, "tools": tool_schemas(), "stream": False, "think": False,
                    "keep_alive": "60m", "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 2048}}
            return post(settings.AAP_OLLAMA_URL + "/api/chat", body, {}, timeout)[0]["message"]
        key = os.environ.get(live["key_env"], "")
        if not key:
            raise ModelError("MODEL_AUTH_FAILED")  # no request is sent without a configured key
        body = {"model": live["model"], "messages": messages, "tools": tool_schemas(), "tool_choice": "auto",
                "temperature": 0.2, "max_completion_tokens": 2048, **live.get("extra", {})}
        while True:
            if throttle:
                throttle.before_request()
            try:
                data, headers = post(live["base_url"] + "/chat/completions", body, {"Authorization": "Bearer " + key},
                                     max(1, throttle.deadline - time.monotonic()) if throttle else timeout)
            except HTTPError as exc:
                if exc.code == 429 and throttle:
                    throttle.rate_limited(exc.headers.get("retry-after"))
                    continue  # same model request again; no tool was executed for it
                raise
            if throttle:
                throttle.after_response(headers, (data.get("usage") or {}).get("total_tokens"))
            return data["choices"][0]["message"]
    except ModelError:
        raise
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, IndexError) as exc:
        raise ModelError(error_code(exc)) from None


def tool_calls(message):
    """Normalize to (call id, tool name, arguments) for either wire format."""
    calls = []
    for index, call in enumerate(message.get("tool_calls") or []):
        function = call.get("function") or {}
        arguments = function.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                pass  # recorded as-is; the guarded service reports INVALID_ARGUMENTS
        calls.append((call.get("id") or f"call_{index}", function.get("name", ""), arguments))
    return calls


def tool_message(call_id, name, outcome):
    if settings.AAP_LIVE["api"] == "ollama":
        return {"role": "tool", "tool_name": name, "content": json.dumps(outcome)}
    return {"role": "tool", "tool_call_id": call_id, "name": name, "content": json.dumps(outcome)}


def assistant_message(message):
    kept = {"role": "assistant", "content": message.get("content") or ""}
    if message.get("tool_calls"):
        kept["tool_calls"] = message["tool_calls"]
    return kept


def run_tool(workspace, result, token, name, arguments):
    try:
        return workspace.execute(str(result.run_id), result.scenario_id, token, name, arguments)
    except ToolAccessError as exc:
        return {"error": str(exc)}  # what the HTTP tool API returns to n8n in the same case


def execute(result, token, workspace):
    snapshot = result.run.input_snapshot
    context = {"destructive_actions_allowed": bool(result.scenario_snapshot.get("destructive_actions_allowed")),
               "max_tool_calls": result.scenario_snapshot.get("max_tool_calls", 12)}
    messages = [{"role": "system", "content": snapshot["system_prompt"]},
                {"role": "user", "content": result.scenario_snapshot["instruction"] + "\nScenario context: "
                    + json.dumps(context, separators=(",", ":"))}]
    deadline = time.monotonic() + BUDGET_SECONDS
    throttle = Throttle(deadline)
    try:
        for _ in range(MAX_ITERATIONS):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ModelError("MODEL_TIMEOUT")
            message = chat(messages, remaining, throttle)
            calls = tool_calls(message)
            messages.append(assistant_message(message))
            if not calls:
                return {"status": "completed", "final_response": (message.get("content") or "")[:16000], "error": None}
            for call_id, name, arguments in calls:
                messages.append(tool_message(call_id, name, run_tool(workspace, result, token, name, arguments)))
        raise ModelError("MODEL_EXECUTION_FAILED")  # iteration ceiling reached without a final answer
    except ModelError as exc:
        return {"status": "failed", "final_response": None, "error": {"code": exc.code}}
