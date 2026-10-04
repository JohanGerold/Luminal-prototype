import pytest


@pytest.mark.django_db
def test_intro_and_direct_workspace_never_dispatch(client, monkeypatch):
    from aap import runs
    from aap.models import EvaluationRun
    monkeypatch.setattr(runs, 'start', lambda *a, **kw: pytest.fail('intro dispatched a model'))
    landing = client.get('/')
    assert landing.status_code == 200
    assert b'id="liminal-intro"' in landing.content
    assert b'Liminal' in landing.content
    assert b'href="/workspace"' in landing.content
    workspace = client.get('/workspace')
    assert workspace.status_code == 200
    assert b'id="liminal-intro"' not in workspace.content
    assert b'Your agents, in focus.' in workspace.content
    assert EvaluationRun.objects.count() == 0


@pytest.mark.django_db
def test_workspace_keeps_saved_filters(client):
    response = client.get('/workspace?mode=DEMO_FALLBACK&days=28')
    assert response.status_code == 200
    assert response.context['execution_mode'] == 'DEMO_FALLBACK'
    assert response.context['days'] == 28
