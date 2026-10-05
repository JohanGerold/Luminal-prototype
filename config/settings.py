import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# Local operator configuration only. Never rendered into browser responses.
if (BASE_DIR / ".env").exists():
    for line in (BASE_DIR / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("AAP_") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(name, value)
SECRET_KEY = os.environ.get("AAP_DJANGO_SECRET_KEY") or secrets.token_urlsafe(48)
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
INSTALLED_APPS = ["django.contrib.contenttypes", "aap"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request", "aap.context.live_provider"]},
}]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("AAP_DB_PATH", str(DATA_DIR / "aap.sqlite3")),
    "OPTIONS": {"timeout": 10},
    # Exercise background-thread concurrency on the same file-backed SQLite
    # behavior as the app, rather than shared-cache in-memory SQLITE_LOCKED.
    "TEST": {"NAME": str(DATA_DIR / "test-aap.sqlite3")},
}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8001", "http://localhost:8001"]
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# LIVE_MODEL provider. Each provider has its own published n8n workflow, so the recorded
# provider/model always describes the workflow that actually ran.
AAP_LIVE_PROVIDERS = {
    # Cloud model, no n8n and no local GPU load: AAP runs the tool-calling loop (aap/direct_agent.py)
    # against Groq's OpenAI-compatible API. Key comes from AAP_GROQ_API_KEY in the ignored .env.
    "groq": {"provider": "Groq (cloud, direct)", "model": "openai/gpt-oss-120b", "webhook_path": None, "api": "openai",
             "base_url": "https://api.groq.com/openai/v1", "key_env": "AAP_GROQ_API_KEY",
             "extra": {"reasoning_effort": "low", "include_reasoning": False}},
    "ollama": {"provider": "Ollama (local)", "model": "qwen3:8b", "webhook_path": "aap-filesystem-agent-ollama"},
    "gemini": {"provider": "Google Gemini", "model": "models/gemini-3-flash-preview", "webhook_path": "aap-filesystem-agent"},
    # Same local model, no n8n. Recorded as a distinct provider so it is never compared with n8n-hosted runs.
    "direct-ollama": {"provider": "Ollama (direct, no n8n)", "model": "qwen3:8b", "webhook_path": None, "api": "ollama"},
}
AAP_LIVE_PROVIDER = os.environ.get("AAP_LIVE_PROVIDER", "groq").strip().lower()
if AAP_LIVE_PROVIDER not in AAP_LIVE_PROVIDERS:
    raise ValueError(f"AAP_LIVE_PROVIDER must be one of: {', '.join(AAP_LIVE_PROVIDERS)}")
AAP_LIVE = AAP_LIVE_PROVIDERS[AAP_LIVE_PROVIDER]
AAP_LIVE_USES_N8N = AAP_LIVE["webhook_path"] is not None
AAP_N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook/" + AAP_LIVE["webhook_path"] if AAP_LIVE_USES_N8N else None
AAP_OLLAMA_URL = os.environ.get("AAP_OLLAMA_URL", "http://127.0.0.1:11434")
AAP_N8N_AUTH_TOKEN = os.environ.get("AAP_N8N_AUTH_TOKEN", "")
