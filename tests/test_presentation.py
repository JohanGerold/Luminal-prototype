import pytest
from django.core.management import call_command

@pytest.mark.django_db
def test_selected_scenario_and_locked_shell(client):
    call_command('seed_demo')
    response = client.get('/runs/new?scenario=controlled-failure')
    assert response.status_code == 200
    assert b'/design-assets/preview.css' in response.content
    assert b'controlled-failure" selected' in response.content
    assert b'id="mode-badge"' in response.content
    assert b'aria-live="polite"' in response.content

@pytest.mark.django_db
def test_saved_runs_empty_and_mode_are_explicit(client):
    from aap.models import EvaluationRun, AgentVersion
    call_command('seed_demo')
    assert b'No saved evaluations yet' in client.get('/runs').content
    run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.first(), execution_mode='DEMO_FALLBACK', status='failed')
    response = client.get('/runs')
    assert response.status_code == 200
    assert b'DEMO_FALLBACK' in response.content
    assert f'/runs/{run.id}/report'.encode() in response.content
    assert b'Not evaluated yet' in response.content
