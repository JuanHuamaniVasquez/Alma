"""Configuración de ALMA. Todo secreto viene del entorno (.env, no versionado)."""
import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
RAIZ = BASE_DIR.parent
load_dotenv(RAIZ / ".env")
if str(RAIZ) not in sys.path:  # el dominio puro (src/) cuelga de la raíz del repo
    sys.path.insert(0, str(RAIZ))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

# Render termina TLS en su proxy; la base remota exige TLS por defecto.
if os.environ.get("RENDER") == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
    SECURE_HSTS_SECONDS = 31536000
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DJANGO_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
]
TERCEROS = ["rest_framework"]
# Una app por módulo del sistema (DOC-01 §1). El dominio puro vive en src/.
APPS_ALMA = [
    "apps.ingesta",       # IN-1..IN-4
    "apps.libro",         # LB-1 (DC-04)
    "apps.motor",         # MO-1..MO-8
    "apps.fabrica",       # FA-1..FA-4 + LA FUNDICIÓN (DC-12)
    "apps.superficies",   # SU-1..SU-5: API REST hacia la vitrina
    "apps.gobernanza",    # GO-1..GO-7: preregistro, epidemiología del error
]
INSTALLED_APPS = DJANGO_APPS + TERCEROS + APPS_ALMA

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = []

DATABASES = {"default": dj_database_url.parse(
    os.environ["DATABASE_URL"],
    conn_max_age=0,
    conn_health_checks=True,
    ssl_require=os.environ.get("DATABASE_SSL_REQUIRE", "1") == "1",
)} if os.environ.get("DATABASE_URL") else {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Timestamps ISO 8601 UTC (CLAUDE.md §3).
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
}

STATIC_URL = "static/"
