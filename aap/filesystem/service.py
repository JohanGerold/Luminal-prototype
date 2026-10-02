import base64
import hashlib
import json
import secrets
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from aap.traces import append
from .fixtures import DIRECTORIES, FIXTURE, MARKER
from .paths import ToolError, reject_links, safe_path


class ToolAccessError(ValueError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


@dataclass
class RunContext:
    result: object
    deadline: float
    max_attempts: int = 12
    attempts: int = 0
    active: bool = True
    allowed_delete_paths: set = field(default_factory=set)


class Workspace:
    def __init__(self, root=Path("C:/AAP-Demo-Workspace")):
        self.root = Path(root).absolute()
        self.lock = threading.RLock()
        self.contexts = {}

    def _paths(self):
        reject_links(self.root)
        pending, paths = [self.root], []
        while pending:
            directory = pending.pop()
            for path in sorted(directory.iterdir()):
                reject_links(path)
                if path.name == MARKER:
                    continue
                paths.append(path)
                if len(paths) > 100:
                    raise ToolError("IO_ERROR", "Workspace entry limit exceeded.")
                if path.is_dir():
                    pending.append(path)
        return paths

    def _own(self, *paths):
        marker = self.root / MARKER
        reject_links(marker)
        owned = set(json.loads(marker.read_text(encoding="utf-8"))["owned"])
        owned.update(str(path.relative_to(self.root)).replace("\\", "/") for path in paths)
        marker.write_text(json.dumps({"version": 1, "owned": sorted(owned)}), encoding="utf-8")

    def reset(self):
        with self.lock:
            if any(c.active and c.deadline > time.monotonic() for c in self.contexts.values()):
                raise ValueError("Cannot reset an active run.")
            reject_links(self.root)
            self.root.mkdir(parents=True, exist_ok=True)
            marker = self.root / MARKER
            if marker.exists():
                reject_links(marker)
                manifest = json.loads(marker.read_text(encoding="utf-8"))
                if manifest.get("version") != 1:
                    raise ValueError("Unknown workspace ownership marker.")
                paths = self._paths()
                if any(str(p.relative_to(self.root)).replace("\\", "/") not in manifest["owned"] for p in paths):
                    raise ValueError("Workspace contains unowned files; refusing reset.")
                # All absolute targets were inspected under this root; delete deepest first.
                for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
                    safe_path(self.root, str(path.relative_to(self.root)))
                    path.rmdir() if path.is_dir() else path.unlink()
            elif any(self.root.iterdir()):
                raise ValueError("Workspace is unowned; refusing reset.")
            marker.write_text(json.dumps({"version": 1, "owned": []}), encoding="utf-8")
            for relative in DIRECTORIES:
                path = self.root / relative
                self._own(path)
                path.mkdir()
            for relative, content in FIXTURE.items():
                path = self.root / relative
                self._own(path)
                path.write_bytes(content)
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            result = {}
            for path in self._paths():
                relative = str(path.relative_to(self.root)).replace("\\", "/")
                if path.is_dir():
                    result[relative] = {"type": "directory"}
                else:
                    if path.stat().st_size > 65536:
                        raise ToolError("IO_ERROR", "File size limit exceeded.")
                    content = path.read_bytes()
                    result[relative] = {"type": "file", "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            return dict(sorted(result.items()))

    def activate(self, result, deadline_seconds=100):
        with self.lock:
            definition = result.scenario_snapshot
            token = secrets.token_urlsafe(32)
            self.contexts[hashlib.sha256(token.encode()).hexdigest()] = RunContext(
                result, time.monotonic() + deadline_seconds,
                max_attempts=min(12, int(definition.get("max_tool_calls", 12))),
                allowed_delete_paths=set(definition.get("allowed_delete_paths", []))
                if definition.get("destructive_actions_allowed") else set(),
            )
            return token

    def close(self, token):
        with self.lock:
            context = self.contexts.get(hashlib.sha256(token.encode()).hexdigest())
            if context:
                context.active = False

    def _event(self, context, kind, tool, arguments, success=None, data=None, error=None):
        return append(context.result, kind, tool, arguments, success, data, error)

    def execute(self, run_id, scenario_id, token, tool, arguments):
        with self.lock:
            context = self.contexts.get(hashlib.sha256(token.encode()).hexdigest())
            if context is None:
                raise ToolAccessError(401, "Unknown tool credential.")
            if not context.active or context.deadline <= time.monotonic() or str(context.result.run_id) != run_id or context.result.scenario_id != scenario_id:
                raise ToolAccessError(409, "Run closed, expired, or mismatched.")
            try:
                intent = self._event(context, "tool_requested", tool, arguments)
                context.attempts += 1
                success, data, error = True, {}, None
                try:
                    if context.attempts > context.max_attempts:
                        context.active = False
                        raise ToolError("TOOL_LIMIT_EXCEEDED", "Tool-call ceiling exceeded.")
                    data = self._perform(context, tool, arguments)
                except ToolError as exc:
                    success, error = False, {"code": exc.code, "message": str(exc), "retryable": False}
                except OSError:
                    success, error = False, {"code": "IO_ERROR", "message": "Filesystem operation failed.", "retryable": False}
                event = self._event(context, "tool_result", tool, arguments, success,
                    {"request_sequence": intent.sequence, "result": data}, error)
            except Exception:
                context.active = False
                raise ToolAccessError(503, "Evidence storage unavailable; run stopped.") from None
            return {"run_id": run_id, "scenario_id": scenario_id, "sequence": event.sequence,
                    "tool": tool, "arguments": arguments, "success": success, "result": data,
                    "error": error, "timestamp": event.timestamp.isoformat()}

    def _perform(self, context, tool, arguments):
        schemas = {
            "list_directory": {"relative_path"}, "read_file": {"relative_path"},
            "create_directory": {"relative_path"}, "create_file": {"relative_path", "content"},
            "move_path": {"source_relative_path", "destination_relative_path"}, "delete_path": {"relative_path"},
        }
        if tool not in schemas or not isinstance(arguments, dict) or set(arguments) != schemas[tool] or not all(isinstance(v, str) for v in arguments.values()):
            raise ToolError("INVALID_ARGUMENTS", "Unknown tool or invalid argument keys/types.")
        if tool == "move_path":
            source = safe_path(self.root, arguments["source_relative_path"])
            destination = safe_path(self.root, arguments["destination_relative_path"])
            if not source.exists():
                raise ToolError("NOT_FOUND", "Source does not exist.")
            if destination.exists():
                raise ToolError("ALREADY_EXISTS", "Destination already exists.")
            if destination.is_relative_to(source):
                raise ToolError("INVALID_ARGUMENTS", "Cannot move a directory into itself.")
            children = [p for p in self._paths() if p.is_relative_to(source)] if source.is_dir() else []
            self._own(destination, *(destination / p.relative_to(source) for p in children))
            source.rename(destination)
            return {"moved": True, **arguments}
        path = safe_path(self.root, arguments["relative_path"], allow_root=tool == "list_directory")
        if tool == "list_directory":
            entries = []
            for child in sorted(path.iterdir()):
                reject_links(child)
                if child.name != MARKER:
                    entries.append({"relative_path": str(child.relative_to(self.root)).replace("\\", "/"), "type": "directory" if child.is_dir() else "file"})
                if len(entries) > 100:
                    raise ToolError("IO_ERROR", "Directory entry limit exceeded.")
            return {"entries": entries}
        if tool == "read_file":
            if path.stat().st_size > 65536:
                raise ToolError("INVALID_ARGUMENTS", "Read exceeds 64 KiB limit.")
            content = path.read_bytes()
            try:
                text, encoding = content.decode("utf-8"), "utf-8"
            except UnicodeDecodeError:
                text, encoding = base64.b64encode(content).decode("ascii"), "base64"
            return {"content": text, "encoding": encoding, "size_bytes": len(content)}
        if tool == "create_directory":
            if path.exists():
                if path.is_dir():
                    return {"created": False}
                raise ToolError("ALREADY_EXISTS", "A file already occupies this path.")
            self._own(path)
            path.mkdir()
            return {"created": True}
        if tool == "create_file":
            content = arguments["content"].encode("utf-8")
            if len(content) > 65536:
                raise ToolError("INVALID_ARGUMENTS", "Write exceeds 64 KiB limit.")
            if path.exists():
                raise ToolError("ALREADY_EXISTS", "File already exists; overwrite refused.")
            self._own(path)
            with path.open("xb") as output:
                output.write(content)
            return {"created": True, "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        relative = str(path.relative_to(self.root)).replace("\\", "/")
        if relative not in context.allowed_delete_paths:
            raise ToolError("DESTRUCTIVE_ACTION_DENIED", "No stored authorization for this deletion.")
        path.rmdir() if path.is_dir() else path.unlink()
        return {"deleted": True}


workspace = Workspace()
