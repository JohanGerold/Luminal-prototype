import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from django.conf import settings
from django.utils.dateparse import parse_datetime

FIELDS = {"contract_version", "run_id", "scenario_id", "execution_mode", "status", "final_response",
          "tool_call_count", "started_at", "completed_at", "error"}


def validate_response(data, run_id, scenario_id):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError("Invalid n8n response fields.")
    if data["contract_version"] != "1" or data["run_id"] != run_id or data["scenario_id"] != scenario_id or data["execution_mode"] != "LIVE_MODEL":
        raise ValueError("Mismatched n8n response identity/mode.")
    if data["status"] not in ("completed", "failed") or (data["status"] == "completed") != (data["error"] is None):
        raise ValueError("Contradictory n8n status/error.")
    if data["final_response"] is not None and (not isinstance(data["final_response"], str) or len(data["final_response"].encode()) > 16384):
        raise ValueError("Invalid final response.")
    dates = [parse_datetime(data[key]) if isinstance(data[key], str) else None for key in ("started_at", "completed_at")]
    if any(date is None or date.tzinfo is None for date in dates) or dates[1] < dates[0]:
        raise ValueError("Invalid n8n timestamps.")
    count = data["tool_call_count"]
    if count is not None and (type(count) is not int or count < 0):
        raise ValueError("Invalid tool-call count.")
    return data


def invoke_agent(result, token):
    run = result.run
    snapshot = run.input_snapshot
    payload = {"contract_version": "1", "run_id": str(run.id), "scenario_id": result.scenario_id,
        "agent_version": snapshot["agent_version"], "system_prompt": snapshot["system_prompt"],
        "instruction": result.scenario_snapshot["instruction"],
        "scenario_context": {"destructive_actions_allowed": bool(result.scenario_snapshot.get("destructive_actions_allowed")),
                             "max_tool_calls": result.scenario_snapshot.get("max_tool_calls", 12)},
        "tool_token": token}
    if not settings.AAP_N8N_AUTH_TOKEN:
        raise ValueError("Local n8n webhook authentication is not configured.")
    request = Request(settings.AAP_N8N_WEBHOOK_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-AAP-Webhook-Token": settings.AAP_N8N_AUTH_TOKEN}, method="POST")
    try:
        with urlopen(request, timeout=95) as response:
            raw = response.read(131073)
        if len(raw) > 131072:
            raise ValueError("n8n response exceeded size limit.")
        return validate_response(json.loads(raw), str(run.id), result.scenario_id)
    except HTTPError as exc:
        raise ValueError(f"n8n execution failed (HTTP {exc.code}); no automatic retry.") from None
    except URLError:
        raise ValueError("n8n unavailable; no automatic retry.") from None
