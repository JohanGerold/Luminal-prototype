import pytest


@pytest.fixture(autouse=True)
def no_real_model_provider(monkeypatch, settings):
    """Tests never reach a real model, whatever the local .env selects or contains.

    LIVE_MODEL defaults to the n8n dispatch path (tests replace invoke_agent), real
    provider keys are removed, and the direct agent's HTTP client fails loudly.
    Tests that exercise the direct loop opt in with their own provider and fake HTTP.
    """
    from aap import direct_agent
    settings.AAP_LIVE = settings.AAP_LIVE_PROVIDERS["ollama"]
    monkeypatch.delenv("AAP_GROQ_API_KEY", raising=False)
    def blocked(*args, **kwargs):
        raise AssertionError("Test attempted a real model request.")
    monkeypatch.setattr(direct_agent, "urlopen", blocked)
