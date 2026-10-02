import json
from pathlib import Path
import pytest


@pytest.fixture
def workspace(tmp_path):
    from aap.filesystem.service import Workspace

    service = Workspace(tmp_path / "demo")
    service.reset()
    return service


@pytest.fixture
def active(workspace, db):
    from django.core.management import call_command
    from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult

    call_command("seed_demo")
    run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.first(), execution_mode="LIVE_MODEL")
    scenario = Scenario.objects.get(pk="normal-organization")
    result = ScenarioResult.objects.create(run=run, scenario=scenario, scenario_snapshot=scenario.definition)
    token = workspace.activate(result)
    return result, token


def invoke(workspace, active, tool, arguments):
    result, token = active
    return workspace.execute(str(result.run_id), result.scenario_id, token, tool, arguments)


@pytest.mark.django_db
def test_real_tools_and_recorded_results(workspace, active):
    assert invoke(workspace, active, "list_directory", {"relative_path": "Downloads"})["success"]
    assert invoke(workspace, active, "read_file", {"relative_path": "Downloads/notes.txt"})["result"]["content"]
    assert invoke(workspace, active, "create_directory", {"relative_path": "Downloads/New"})["success"]
    assert invoke(workspace, active, "create_file", {"relative_path": "Downloads/New/example.txt", "content": "hello"})["success"]
    moved = invoke(workspace, active, "move_path", {"source_relative_path": "Downloads/New/example.txt", "destination_relative_path": "Archive/example.txt"})
    assert moved["success"]
    assert (workspace.root / "Archive/example.txt").read_text() == "hello"
    # A server-owned authority snapshot permits this test deletion.
    workspace.contexts[next(iter(workspace.contexts))].allowed_delete_paths = {"Archive/example.txt"}
    assert invoke(workspace, active, "delete_path", {"relative_path": "Archive/example.txt"})["success"]
    assert not (workspace.root / "Archive/example.txt").exists()
    events = list(active[0].events.all())
    assert len(events) == 12
    assert [event.sequence for event in events] == list(range(1, 13))
    assert events[-1].kind == "tool_result" and events[-1].success
    workspace.close(active[1])
    workspace.reset()
    assert len(list((workspace.root / "Downloads").iterdir())) == 5


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["../outside.txt", "Downloads/../../outside.txt", "C:\\Windows", "C:outside.txt", "\\\\host\\share", "/outside", "Downloads/file:stream", "Downloads/CON"])
def test_escape_attempts_are_refused_and_logged(workspace, active, path):
    sentinel = workspace.root.parent / "outside.txt"
    sentinel.write_text("untouched")
    response = invoke(workspace, active, "read_file", {"relative_path": path})
    assert not response["success"]
    assert response["error"]["code"] == "BOUNDARY_REJECTED"
    assert sentinel.read_text() == "untouched"
    assert active[0].events.filter(kind="tool_result", success=False).count() == 1


@pytest.mark.django_db
def test_unauthorized_delete_and_root_mutation_are_blocked(workspace, active):
    response = invoke(workspace, active, "delete_path", {"relative_path": "Downloads/notes.txt"})
    assert response["error"]["code"] == "DESTRUCTIVE_ACTION_DENIED"
    assert (workspace.root / "Downloads/notes.txt").exists()
    assert invoke(workspace, active, "delete_path", {"relative_path": "."})["error"]["code"] == "BOUNDARY_REJECTED"
    with pytest.raises(ValueError, match="active"):
        workspace.reset()


@pytest.mark.django_db
def test_link_escape_is_blocked(workspace, active, tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    (external / "secret.txt").write_text("untouched")
    link = workspace.root / "Downloads/link"
    # Windows junction creation needs no symlink privilege.
    import subprocess
    created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(external)], capture_output=True)
    assert created.returncode == 0, created.stderr
    try:
        response = invoke(workspace, active, "read_file", {"relative_path": "Downloads/link/secret.txt"})
        assert response["error"]["code"] == "BOUNDARY_REJECTED"
        assert (external / "secret.txt").read_text() == "untouched"
    finally:
        link.rmdir()


def test_reset_refuses_unowned_files(workspace):
    (workspace.root / "Downloads/foreign.txt").write_text("preserve")
    with pytest.raises(ValueError, match="unowned"):
        workspace.reset()
    assert (workspace.root / "Downloads/foreign.txt").read_text() == "preserve"


@pytest.mark.django_db
def test_tool_api_binding_limits_and_closed_token(workspace, active, client, monkeypatch):
    import aap.api
    monkeypatch.setattr(aap.api, "workspace", workspace)
    result, token = active
    envelope = {"run_id": str(result.run_id), "scenario_id": result.scenario_id,
                "arguments": {"relative_path": "Downloads"}}
    url = "/api/tools/list_directory"
    auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    assert client.post(url, json.dumps(envelope), content_type="application/json").status_code == 401
    assert client.post(url, json.dumps(envelope), content_type="application/json", **auth).json()["success"]
    envelope["root"] = str(workspace.root.parent)
    assert client.post(url, json.dumps(envelope), content_type="application/json", **auth).status_code == 400
    del envelope["root"]
    envelope["scenario_id"] = "other"
    assert client.post(url, json.dumps(envelope), content_type="application/json", **auth).status_code == 409
    workspace.close(token)
    envelope["scenario_id"] = result.scenario_id
    assert client.post(url, json.dumps(envelope), content_type="application/json", **auth).status_code == 409
