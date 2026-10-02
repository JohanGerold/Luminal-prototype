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
    "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
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
AAP_N8N_WEBHOOK_URL = os.environ.get("AAP_N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/aap-filesystem-agent")
AAP_N8N_AUTH_TOKEN = os.environ.get("AAP_N8N_AUTH_TOKEN", "")
