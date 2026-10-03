import threading
import time
import pytest
from django.core.management import call_command
from django.test import Client


@pytest.fixture
def runner(tmp_path, monkeypatch, transactional_db):
    from aap import runs
    from aap.filesystem.service import Workspace
    call_command("seed_demo")
    monkeypatch.setattr(runs, "workspace", Workspace(tmp_path / "demo"))
    return runs


def wait_terminal(run):
    for _ in range(200):
        run.refresh_from_db()
        if run.completed_at:
            return
        time.sleep(.01)
    pytest.fail("Runner did not finish")


def test_double_start_reset_conflict_and_recorded_effect(runner, monkeypatch):
    entered, release = threading.Event(), threading.Event()
    def model(result, token):
        entered.set()
        assert release.wait(3)
        runner.workspace.execute(str(result.run_id), result.scenario_id, token,
            "move_path", {"source_relative_path": "Downloads/notes.txt", "destination_relative_path": "Archive/notes.txt"})
        return {"status": "completed", "final_response": "Moved."}
    monkeypatch.setattr(runner, "invoke_agent", model)
    client = Client()
    payload = {"agent_version": "v1", "scenario_id": "normal-organization", "execution_mode": "LIVE_MODEL"}
    response = client.post("/api/runs", payload, content_type="application/json")
    assert response.status_code == 202
    assert entered.wait(2)
    try:
        assert client.post("/api/runs", payload, content_type="application/json").status_code == 409
        assert client.post("/api/reset").status_code == 409
    finally:
        release.set()
    from aap.models import EvaluationRun
    run = EvaluationRun.objects.get(pk=response.json()["run_id"])
    wait_terminal(run)
    assert run.status == "completed"
    result = run.results.get()
    assert result.evidence_complete and "Archive/notes.txt" in result.after
    status = client.get(f"/api/runs/{run.id}").json()
    assert status["execution_mode"] == "LIVE_MODEL" and status["tool_call_count"] == 1
    assert "token" not in str(status).lower()
    assert client.post("/api/reset").status_code == 200


def test_timeout_closes_tools_and_preserves_snapshot(runner, monkeypatch):
    from aap.filesystem.service import ToolAccessError
    entered, release, late = threading.Event(), threading.Event(), threading.Event()
    monkeypatch.setattr(runner, "RUN_SECONDS", .08)
    def model(result, token):
        entered.set()
        assert release.wait(3)
        with pytest.raises(ToolAccessError) as exc:
            runner.workspace.execute(str(result.run_id), result.scenario_id, token,
                "delete_path", {"relative_path": "Downloads/notes.txt"})
        assert exc.value.status == 409
        late.set()
        return {"status": "completed", "final_response": "late"}
    monkeypatch.setattr(runner, "invoke_agent", model)
    run = runner.start("v1", "normal-organization", "LIVE_MODEL")
    assert entered.wait(2)
    wait_terminal(run)
    assert run.status == "timed_out"
    result = run.results.get()
    assert not result.evidence_complete and result.before == result.after
    release.set()
    assert late.wait(2)
    run.refresh_from_db()
    assert run.status == "timed_out" and run.results.get().final_response == ""


def test_explicit_mode_and_csrf(runner):
    client = Client()
    assert client.post("/api/runs", {"agent_version": "v1", "scenario_id": "normal-organization"}, content_type="application/json").status_code == 400
    assert Client(enforce_csrf_checks=True).post("/api/reset").status_code == 403


def test_restart_marks_interrupted_without_redispatch(runner):
    from aap.models import EvaluationRun, AgentVersion
    run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.first(), execution_mode="LIVE_MODEL", status="executing")
    runner.recover_interrupted()
    run.refresh_from_db()
    assert run.status == "interrupted" and run.completed_at and run.error


def test_rate_limit_after_real_tool_effects_preserves_uncertain_evidence(runner, monkeypatch):
    """Isolated test DB, no network: reproduce the saved partial-cleanup shape."""
    import json
    from pathlib import Path
    from aap.filesystem.service import ToolAccessError
    tokens = []
    dispatches = []
    actions = json.loads((Path(__file__).parents[1] / 'aap/seeds/fallback_actions.json').read_text())['normal-organization']
    def model(result, token):
        dispatches.append(result.run_id)
        tokens.append(token)
        for path in ('.', 'Downloads', 'Archive'):
            runner.workspace.execute(str(result.run_id), result.scenario_id, token, 'list_directory', {'relative_path': path})
        for tool, args in actions:
            assert runner.workspace.execute(str(result.run_id), result.scenario_id, token, tool, args)['success']
        return {'status': 'failed', 'error': {'code': 'MODEL_RATE_LIMIT'}}
    monkeypatch.setattr(runner, 'invoke_agent', model)
    run = runner.start('v2', 'ambiguous-cleanup', 'LIVE_MODEL')
    wait_terminal(run)
    result = run.results.get()
    assert dispatches == [run.pk]
    assert run.status == 'failed' and run.error['code'] == 'MODEL_RATE_LIMIT'
    assert run.input_snapshot['execution_limits'] == {'run_seconds': runner.RUN_SECONDS}
    assert result.verdict == 'UNCERTAIN' and not result.evidence_complete, result.findings
    assert result.before != result.after and 'Downloads/Documents/notes.txt' in result.after
    assert result.events.filter(kind='tool_requested').count() == 11
    assert result.events.filter(kind='tool_result', tool='move_path', success=True).count() == 5
    with pytest.raises(ToolAccessError) as exc:
        runner.workspace.execute(str(run.pk), result.scenario_id, tokens[0], 'delete_path', {'relative_path': 'Downloads/Documents/notes.txt'})
    assert exc.value.status == 409
    client = Client()
    for url in (f'/runs/{run.pk}/report', '/runs', '/'):
        response = client.get(url)
        assert response.status_code == 200
        assert b'MODEL_RATE_LIMIT' in response.content and b'UNCERTAIN' in response.content
        assert b'LIVE_MODEL' in response.content
    assert client.get(f'/runs/{run.pk}/trace').status_code == 200
