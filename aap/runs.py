"""One bounded in-process execution. Never redispatch a lost model response."""
import queue
import threading
from django.db import close_old_connections
from django.utils import timezone
from aap.filesystem.service import workspace
from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult
from aap.n8n_client import invoke_agent
from aap.traces import append
from aap.evaluation import evaluate_result
from aap import fallback

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
    if mode not in ("LIVE_MODEL", "DEMO_FALLBACK"):
        raise ValueError("Select an execution mode explicitly.")
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
                "execution_limits": {"run_seconds": RUN_SECONDS},
                "provider": "Google Gemini" if mode == 'LIVE_MODEL' else None,
                "model": "models/gemini-3-flash-preview" if mode == 'LIVE_MODEL' else None,
                "fallback_script_version": fallback.SCRIPT_VERSION if mode == 'DEMO_FALLBACK' else None})
        result = ScenarioResult.objects.create(run=run, scenario=scenario,
            scenario_snapshot={**scenario.definition, "instruction": scenario.instruction}, before=before)
        with workspace.lock:
            append(result, "run_started", data={"execution_mode": mode, "agent_version": version.version})
            append(result, "user_instruction", data={"instruction": scenario.instruction})
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
        mailbox.put(invoke_agent(result, token) if result.run.execution_mode == 'LIVE_MODEL' else fallback.execute(result, token, workspace))
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
                code = (response.get('error') or {}).get('code') if response else None
                if code not in {'MODEL_RATE_LIMIT', 'MODEL_AUTH_FAILED', 'MODEL_TIMEOUT', 'MODEL_REQUEST_REJECTED', 'MODEL_UNAVAILABLE'}:
                    code = 'MODEL_EXECUTION_FAILED'
                run.error = {"code": code, "message": "Model execution failed; inspect recorded tools. No automatic retry."}
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
        evaluate_result(result)
        with workspace.lock:
            if result.final_response:
                append(result, "final_response", data={"text": result.final_response})
            append(result, "run_finished", data={"status": run.status, "evidence_complete": result.evidence_complete}, error=run.error)
        run.completed_at = timezone.now()
        run.save()
    finally:
        workspace.close(token)
        active_lock.release()
        close_old_connections()


def recover_interrupted():
    """Called only before starting the single app process; never resume execution."""
    interrupted = list(EvaluationRun.objects.filter(status__in=["preparing", "executing"]).values_list('pk', flat=True))
    EvaluationRun.objects.filter(pk__in=interrupted).update(
        status="interrupted", completed_at=timezone.now(),
        error={"code": "APP_RESTART", "message": "App restarted; execution was not resumed and evidence may be incomplete."})
    for result in ScenarioResult.objects.select_related('run').filter(run_id__in=interrupted):
        result.evidence_complete = False
        result.save(update_fields=['evidence_complete'])
        evaluate_result(result)
