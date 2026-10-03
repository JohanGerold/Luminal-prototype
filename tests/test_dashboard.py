from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone


@pytest.fixture
def catalog(db):
    from aap.models import AgentVersion, Scenario
    call_command('seed_demo')
    return AgentVersion.objects.first(), Scenario.objects.get(pk='single-action')


def record(catalog, mode='LIVE_MODEL', verdict='PASS', status='completed', days=0, duration=8):
    from aap.models import EvaluationRun, ScenarioResult, TraceEvent
    now = timezone.now() - timedelta(days=days)
    run = EvaluationRun.objects.create(agent_version=catalog[0], execution_mode=mode,
        status=status, started_at=now, completed_at=None if status == 'executing' else now + timedelta(seconds=duration),
        input_snapshot={'agent_version': 'saved-v2'})
    EvaluationRun.objects.filter(pk=run.pk).update(created_at=now)
    result = ScenarioResult.objects.create(run=run, scenario=catalog[1], verdict=verdict)
    TraceEvent.objects.create(result=result, sequence=1, kind='tool_requested', tool='create_file')
    TraceEvent.objects.create(result=result, sequence=2, kind='tool_result', tool='create_file', success=True)
    return run


def test_overview_uses_saved_results_without_dispatch(client, catalog, monkeypatch):
    from aap import runs, evaluation
    monkeypatch.setattr(runs, 'start', lambda *a: pytest.fail('overview dispatched'))
    monkeypatch.setattr(evaluation, 'evaluate', lambda **kw: pytest.fail('overview evaluated'))
    record(catalog)
    record(catalog, verdict='UNCERTAIN', status='failed', duration=12)
    record(catalog, verdict=None, status='executing')
    record(catalog, mode='DEMO_FALLBACK', verdict='FAIL')
    response = client.get('/')
    assert response.status_code == 200
    data = response.context
    assert data['total'] == 3
    assert data['evaluated'] == 2
    assert data['passed'] == 1 and data['uncertain'] == 1 and data['failed'] == 0
    assert data['pass_rate'] == 50
    assert data['average_duration'] == 10
    assert sum(day['total'] for day in data['chart_days']) == 3
    assert sum(day['passed'] for day in data['chart_days']) == 1
    assert b'monochrome.js' not in response.content
    assert b'Illustrative data' not in response.content


def test_overview_mode_and_window_are_explicit(client, catalog):
    record(catalog, days=10)
    fallback = record(catalog, mode='DEMO_FALLBACK', verdict='FAIL')
    assert client.get('/').context['total'] == 0
    assert client.get('/?days=28').context['total'] == 1
    response = client.get('/?mode=DEMO_FALLBACK')
    assert response.context['total'] == 1 and response.context['failed'] == 1
    assert response.context['execution_mode'] == 'DEMO_FALLBACK'
    assert f'/runs/{fallback.id}/report'.encode() in response.content
    assert response.context['scenario_rows'][-1]['version'] == 'saved-v2'
    assert response.context['scenario_rows'][-1]['tool_count'] == 1


def test_overview_empty_history_does_not_invent_metrics(client, catalog):
    response = client.get('/?mode=invalid&days=999')
    assert response.status_code == 200
    assert response.context['execution_mode'] == 'LIVE_MODEL'
    assert response.context['days'] == 7
    assert response.context['pass_rate'] is None
    assert response.context['average_duration'] is None
    assert len(response.context['scenario_rows']) == 6
    assert all(row['run'] is None for row in response.context['scenario_rows'])
    assert b'No saved activity' in response.content
    assert b'Not run' in response.content
