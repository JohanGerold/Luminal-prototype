import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .filesystem.service import ToolAccessError, workspace


@csrf_exempt
@require_POST
def tool(request, tool):
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return JsonResponse({"error": "Tool credential required."}, status=401)
    if len(request.body) > 131072:
        return JsonResponse({"error": "Request too large."}, status=400)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict) or set(data) != {"run_id", "scenario_id", "arguments"}:
            raise ValueError()
        if not isinstance(data["run_id"], str) or not isinstance(data["scenario_id"], str):
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid tool envelope."}, status=400)
    try:
        return JsonResponse(workspace.execute(data["run_id"], data["scenario_id"], authorization[7:], tool, data["arguments"]))
    except ToolAccessError as exc:
        return JsonResponse({"error": str(exc)}, status=exc.status)
