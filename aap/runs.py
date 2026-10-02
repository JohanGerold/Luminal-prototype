"""One bounded in-process execution. Never redispatch a lost model response."""
import queue
import threading
from django.db import close_old_connections
from django.utils import timezone
from aap.filesystem.service import workspace
from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult
from aap.n8n_client import invoke_agent

RUN_SECONDS = 100
active_lock = threading.Lock()


class Busy(ValueError):
    pass


def reset():
    if not active_lock.acquire(blocking=False):
        raise Busy("A scenario is running; reset is unavailable.")
    try:
        return workspace.reset()
    finally:
        active_lock.release()


def start(version_name, scenario_id, mode):
    if mode != "LIVE_MODEL":
        raise ValueError("Select LIVE_MODEL explicitly. Fallback is not implemented yet.")
    version = AgentVersion.objects.get(agent_id="file-organization", version=version_name)
    scenario = Scenario.objects.get(pk=scenario_id)
    if not active_lock.acquire(blocking=False):
        raise Busy("A scenario is already running.")
    run, token = None, None
    try:
        before = workspace.reset()
        run = EvaluationRun.objects.create(agent_version=version, execution_mode=mode, status="executing",
            started_at=timezone.now(), input_snapshot={"agent_version": version.version,
                "system_prompt": version.system_prompt, "tools": version.tools,
                "provider": "Google Gemini", "model": "models/gemini-3-flash-preview"})
        result = ScenarioResult.objects.create(run=run, scenario=scenario,
            scenario_snapshot={**scenario.definition, "instruction": scenario.instruction}, before=before)
        token = workspace.activate(result, deadline_seconds=RUN_SECONDS)
        threading.Thread(target=_execute, args=(result.pk, token), daemon=True).start()
        return run
    except Exception:
        if token:
            workspace.close(token)
        if run:
            run.status, run.completed_at = "failed", timezone.now()
            run.error = {"code": "PREPARATION_FAILED", "message": "Run preparation failed; no automatic retry."}
            run.save()
        active_lock.release()
        raise


def _dispatch(result, token, mailbox):
    close_old_connections()
    try:
        mailbox.put(invoke_agent(result, token))
    except Exception:
        # Provider response bodies and credentials never enter app error logs.
        mailbox.put(None)
    finally:
        close_old_connections()


def _execute(result_id, token):
    close_old_connections()
    try:
        result = ScenarioResult.objects.select_related("run").get(pk=result_id)
        run = result.run
        mailbox = queue.Queue(maxsize=1)
        threading.Thread(target=_dispatch, args=(result, token, mailbox), daemon=True).start()
        try:
            response = mailbox.get(timeout=RUN_SECONDS)
            if response and response["status"] == "completed":
                result.final_response = response["final_response"] or ""
                run.status = "completed"
            else:
                run.status = "failed"
                run.error = {"code": "MODEL_EXECUTION_FAILED", "message": "Model execution failed; inspect recorded tools. No automatic retry."}
        except queue.Empty:
            run.status = "timed_out"
            run.error = {"code": "RUN_TIMEOUT", "message": "Run deadline exceeded; tools closed. No automatic retry."}
        # Closure serializes with tool execution before the final state is read.
        workspace.close(token)
        try:
            result.after = workspace.snapshot()
            result.evidence_complete = run.status == "completed" and result.events.filter(kind="tool_requested").count() == result.events.filter(kind="tool_result").count()
        except Exception:
            result.evidence_complete = False
            run.status = "failed"
            run.error = {"code": "SNAPSHOT_FAILED", "message": "Final state unavailable; evidence is incomplete."}
        result.save()
        run.completed_at = timezone.now()
        run.save()
    finally:
        workspace.close(token)
        active_lock.release()
        close_old_connections()


def recover_interrupted():
    """Called only before starting the single app process; never resume execution."""
    EvaluationRun.objects.filter(status__in=["preparing", "executing"]).update(
        status="interrupted", completed_at=timezone.now(),
        error={"code": "APP_RESTART", "message": "App restarted; execution was not resumed and evidence may be incomplete."})
