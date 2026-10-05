import pytest
from django.conf import settings
from django.test import Client

from tests.test_reporting import saved_run  # noqa: F401
from tests.test_runs import runner, wait_terminal  # noqa: F401


def test_configured_provider_selects_its_own_runtime():
    live = settings.AAP_LIVE_PROVIDERS[settings.AAP_LIVE_PROVIDER]
    assert settings.AAP_LIVE is live
    if live["webhook_path"]:
        assert settings.AAP_N8N_WEBHOOK_URL == "http://127.0.0.1:5678/webhook/" + live["webhook_path"]
    else:
        assert settings.AAP_N8N_WEBHOOK_URL is None and live["api"] in ("ollama", "openai")
    paths = [item["webhook_path"] for item in settings.AAP_LIVE_PROVIDERS.values() if item["webhook_path"]]
    assert len(paths) == len(set(paths))
    labels = [item["provider"] for item in settings.AAP_LIVE_PROVIDERS.values()]
    assert len(labels) == len(set(labels))  # distinct labels keep comparison from pairing different runtimes


@pytest.mark.parametrize("name", ["ollama", "gemini"])
def test_live_run_records_the_configured_provider_and_model(runner, monkeypatch, name):  # noqa: F811
    live = settings.AAP_LIVE_PROVIDERS[name]
    monkeypatch.setattr(settings, "AAP_LIVE", live)
    monkeypatch.setattr(runner, "invoke_agent", lambda result, token: {"status": "completed", "final_response": "Done."})
    run = runner.start("v1", "single-action", "LIVE_MODEL")
    wait_terminal(run)
    assert (run.input_snapshot["provider"], run.input_snapshot["model"]) == (live["provider"], live["model"])


def test_report_shows_recorded_provider_not_current_setting(client, saved_run, monkeypatch):  # noqa: F811
    saved_run.input_snapshot["provider"] = "Google Gemini"
    saved_run.save()
    monkeypatch.setattr(settings, "AAP_LIVE", settings.AAP_LIVE_PROVIDERS["ollama"])
    body = client.get(f"/runs/{saved_run.id}/report").content.decode()
    assert "Google Gemini · models/gemini-3-flash-preview" in body


def test_start_page_names_configured_live_provider(db, monkeypatch):
    monkeypatch.setattr(settings, "AAP_LIVE", settings.AAP_LIVE_PROVIDERS["ollama"])
    body = Client().get("/runs/new").content.decode()
    assert "LIVE_MODEL — Ollama (local) · qwen3:8b" in body
    assert "Google Gemini" not in body
