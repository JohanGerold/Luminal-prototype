import pytest
from django.core.management import call_command
from tests.test_runs import wait_terminal


@pytest.mark.django_db(transaction=True)
def test_outage_fallback_is_fresh_and_never_relabels_live(tmp_path, monkeypatch):
    from aap import runs
    from aap.filesystem.service import Workspace
    call_command('seed_demo')
    monkeypatch.setattr(runs, 'workspace', Workspace(tmp_path / 'demo'))
    def unavailable(*args):
        raise ConnectionError('Provider unavailable')
    monkeypatch.setattr(runs, 'invoke_agent', unavailable)
    live = runs.start('v1', 'normal-organization', 'LIVE_MODEL')
    wait_terminal(live)
    assert live.status == 'failed' and live.results.get().verdict == 'UNCERTAIN'
    fallback = runs.start('v1', 'normal-organization', 'DEMO_FALLBACK')
    wait_terminal(fallback)
    assert fallback.id != live.id and fallback.execution_mode == 'DEMO_FALLBACK'
    assert fallback.status == 'completed' and fallback.results.get().verdict == 'PASS'
    assert fallback.results.get().events.filter(kind='tool_requested').count() == 8
    live.refresh_from_db()
    assert live.execution_mode == 'LIVE_MODEL' and live.status == 'failed'


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('scenario,category', [
    ('boundary-attempt', 'ATTEMPTED_BOUNDARY_VIOLATION'),
    ('all-pdfs', 'INCOMPLETE_TASK'),
])
def test_scripted_failures_are_observed_not_forced(tmp_path, monkeypatch, scenario, category):
    from aap import runs
    from aap.filesystem.service import Workspace
    from aap.story import project
    call_command('seed_demo')
    monkeypatch.setattr(runs, 'workspace', Workspace(tmp_path / 'demo'))
    monkeypatch.setattr(runs, 'invoke_agent', lambda *a: pytest.fail('No model call allowed'))
    run = runs.start('v2', scenario, 'DEMO_FALLBACK')
    wait_terminal(run)
    result = run.results.get()
    assert result.verdict == 'FAIL'
    assert any(f['category'] == category and f['proven'] for f in result.findings)
    assert project(run)['steps'][-1]['title'] == 'FAIL'
    if scenario == 'boundary-attempt':
        assert result.before == result.after
        assert 'script stopped' in project(run)['interruption']
    else:
        assert 'Downloads/invoice.pdf' in result.after
        assert 'Downloads/PDFs/assignment.pdf' in result.after
