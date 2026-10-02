import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
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
}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8001", "http://localhost:8001"]
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
