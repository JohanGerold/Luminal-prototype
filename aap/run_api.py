import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from . import runs
from .models import EvaluationRun


@require_POST
def start(request):
    try:
        if len(request.body) > 4096:
            raise ValueError("Request too large.")
        data = json.loads(request.body)
        if not isinstance(data, dict) or set(data) != {"agent_version", "scenario_id", "execution_mode"} or not all(isinstance(v, str) for v in data.values()):
            raise ValueError("Select agent version, scenario and execution mode.")
        run = runs.start(data["agent_version"], data["scenario_id"], data["execution_mode"])
        return JsonResponse({"run_id": str(run.id), "url": f"/runs/{run.id}"}, status=202)
    except runs.Busy as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    except (ValueError, ObjectDoesNotExist):
        return JsonResponse({"error": "Invalid selection or fixture cannot be reset safely."}, status=400)
    except Exception:
        return JsonResponse({"error": "Run preparation failed. Inspect local configuration; no automatic retry."}, status=503)


@require_POST
def reset(request):
    try:
        return JsonResponse({"state": runs.reset()})
    except runs.Busy as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    except Exception:
        return JsonResponse({"error": "Reset refused; check workspace ownership and contents."}, status=409)


@require_GET
def status(request, run_id):
    run = get_object_or_404(EvaluationRun, pk=run_id)
    result = run.results.first()
    events = list(result.events.values("sequence", "timestamp", "kind", "tool", "arguments", "success", "data", "error")) if result else []
    return JsonResponse({"run_id": str(run.id), "execution_mode": run.execution_mode, "status": run.status,
        "agent_version": run.input_snapshot.get("agent_version"), "model": run.input_snapshot.get("model"),
        "started_at": run.started_at, "completed_at": run.completed_at, "error": run.error,
        "tool_call_count": sum(e["kind"] == "tool_requested" for e in events), "events": events,
        "before": result.before if result else {}, "after": result.after if result else {},
        "final_response": result.final_response if result else "", "evidence_complete": bool(result and result.evidence_complete),
        "verdict": result.verdict if result else None, "assertions": result.assertions if result else [],
        "findings": result.findings if result else [], "evaluation_metadata": result.evaluation_metadata if result else {}})
