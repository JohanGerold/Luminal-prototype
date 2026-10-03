from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Agent, Scenario, AgentVersion, EvaluationRun


def home(request):
    from .dashboard import overview
    return render(request, 'dashboard.html', overview(request.GET.get('mode'), request.GET.get('days')))


def compare(request):
    from .comparison import project
    return render(request, 'compare.html', project(request.GET.get('mode')))


def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"service": "aap-prototype", "database": "ready"})


def agents(request):
    return render(request, "agents.html", {"agents": Agent.objects.all()})


def agent_detail(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    return render(request, "agent.html", {"agent": agent, "versions": agent.versions.order_by("version")})


def scenarios(request):
    return render(request, "scenarios.html", {"scenarios": Scenario.objects.all()})


def new_run(request):
    scenarios = list(Scenario.objects.all())
    return render(request, "new_run.html", {"versions": AgentVersion.objects.order_by("version"), "scenarios": scenarios,
        "selected_scenario": request.GET.get("scenario"), "scenario_catalog": {item.id: item.instruction for item in scenarios}})


def run_detail(request, run_id):
    return render(request, "run.html", {"run": get_object_or_404(EvaluationRun, pk=run_id)})


def trace(request, run_id):
    from .traces import rows
    run = get_object_or_404(EvaluationRun, pk=run_id)
    result = run.results.first()
    return render(request, "trace.html", {"run": run, "events": rows(result) if result else []})


def design_preview(request):
    # A visual-review surface only: no database reads or evaluation dispatch.
    return render(request, 'design_preview.html')


def report(request, run_id):
    from .reporting import project
    run = get_object_or_404(EvaluationRun.objects.select_related('agent_version__agent'), pk=run_id)
    return render(request, 'report.html', project(run))


def saved_runs(request):
    records = EvaluationRun.objects.select_related('agent_version').prefetch_related('results__scenario').order_by('-created_at')[:50]
    rows = []
    for run in records:
        result = next(iter(run.results.all()), None)
        rows.append({'run': run, 'scenario': result.scenario.name if result else None,
            'version': run.input_snapshot.get('agent_version', run.agent_version.version),
            'verdict': result.verdict if result else None})
    return render(request, 'saved_runs.html', {'rows': rows})
