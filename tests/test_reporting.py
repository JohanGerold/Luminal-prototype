from datetime import timedelta
import pytest
from django.core.management import call_command
from django.utils import timezone


@pytest.fixture
def saved_run(db):
    from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult, TraceEvent
    call_command('seed_demo')
    started = timezone.now()
    run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.first(),
        execution_mode='LIVE_MODEL', status='failed', started_at=started,
        completed_at=started + timedelta(seconds=2.5),
        input_snapshot={'agent_version': 'historical-v1', 'model': 'models/gemini-3-flash-preview', 'tools': ['read_file']},
        error={'code': 'MODEL_RATE_LIMIT', 'message': 'Model unavailable.'})
    result = ScenarioResult.objects.create(run=run, scenario=Scenario.objects.get(pk='single-action'),
        scenario_snapshot={'instruction': '<script>alert(1)</script>'}, verdict='UNCERTAIN',
        before={'Downloads/a.txt': {'type': 'file', 'sha256': 'before'}},
        after={'Downloads/a.txt': {'type': 'file', 'sha256': 'after'}},
        assertions=[{'name': 'File preserved', 'passed': None, 'operands': {}, 'evidence': [{'event_sequence': 1}, {'state': 'after', 'path': 'Downloads/a.txt'}]}],
        evaluation_metadata={'evaluator_version': 'saved-rules', 'missing_evidence': ['Final response missing.']})
    TraceEvent.objects.create(result=result, sequence=1, kind='tool_requested', tool='read_file')
    TraceEvent.objects.create(result=result, sequence=2, kind='tool_result', tool='read_file', success=False)
    return run


def test_report_projects_saved_evidence_without_execution(saved_run, monkeypatch):
    from aap.reporting import project
    from aap import runs, evaluation
    monkeypatch.setattr(runs, 'start', lambda *a: pytest.fail('report dispatched'))
    monkeypatch.setattr(evaluation, 'evaluate', lambda **kw: pytest.fail('report re-evaluated'))
    report = project(saved_run)
    assert report['verdict'] == 'UNCERTAIN'
    assert report['tool_count'] == 1
    assert report['duration'] == 2.5
    assert report['version'] == 'historical-v1'
    assert report['state_rows'][0]['change'] == 'Changed'
    assert report['assertions'][0]['evidence'][0]['url'].endswith('/trace#event-1')
    assert report['assertions'][0]['evidence'][1]['url'] == '#state-0'


def test_report_route_escapes_and_separates_status_verdict(client, saved_run):
    response = client.get(f'/runs/{saved_run.pk}/report')
    assert response.status_code == 200
    for content in (b'LIVE_MODEL', b'UNCERTAIN', b'MODEL_RATE_LIMIT', b'historical-v1', b'Execution status', b'failed'):
        assert content in response.content
    assert b'&lt;script&gt;alert(1)&lt;/script&gt;' in response.content
    assert b'<script>alert(1)</script>' not in response.content


def test_pending_report_does_not_invent_duration_or_verdict(client, saved_run):
    from aap.reporting import project
    saved_run.status = 'executing'
    saved_run.completed_at = None
    saved_run.results.all().delete()
    saved_run.save()
    report = project(saved_run)
    assert report['verdict'] is None
    assert report['duration'] is None
    assert client.get(f'/runs/{saved_run.pk}/report').status_code == 200


def test_fallback_report_remains_explicit(client, saved_run):
    saved_run.execution_mode = 'DEMO_FALLBACK'
    saved_run.save()
    response = client.get(f'/runs/{saved_run.pk}/report')
    assert b'DEMO_FALLBACK' in response.content
    assert b'Scripted execution' in response.content


def test_unavailable_after_snapshot_never_claims_removal(saved_run):
    from aap.reporting import project
    result = saved_run.results.get()
    result.after = {}
    result.save()
    row = project(saved_run)['state_rows'][0]
    assert row['change'] == 'Not established'
    assert row['after'] == 'Snapshot unavailable'
