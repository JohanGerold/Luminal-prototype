import subprocess
import sys
from pathlib import Path
import pytest


def test_app_entrypoint_exists():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parents[1] / "manage.py"), "check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.django_db
def test_seed_is_idempotent_and_agent_configuration_renders(client):
    from django.core.management import call_command
    from aap.models import Agent, AgentVersion, Scenario

    call_command("seed_demo")
    call_command("seed_demo")
    assert Agent.objects.count() == 1
    assert AgentVersion.objects.count() == 2
    assert Scenario.objects.count() == 1
    response = client.get("/agents/file-organization")
    assert response.status_code == 200
    for text in ("File Organization Agent", "System prompt", "move_path", "Version v1", "Version v2"):
        assert text in response.content.decode()
    assert client.get("/health").json()["database"] == "ready"


@pytest.mark.django_db
def test_run_cannot_be_saved_without_explicit_execution_mode():
    from django.core.management import call_command
    from django.db import IntegrityError, transaction
    from aap.models import AgentVersion, EvaluationRun

    call_command("seed_demo")
    version = AgentVersion.objects.first()
    with pytest.raises(IntegrityError), transaction.atomic():
        EvaluationRun.objects.create(agent_version=version)
    for mode in ("LIVE_MODEL", "DEMO_FALLBACK"):
        assert EvaluationRun.objects.create(agent_version=version, execution_mode=mode).execution_mode == mode
