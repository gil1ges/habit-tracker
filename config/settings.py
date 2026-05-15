"""
Django settings for Habit Tracker project.
"""

import os
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(os.getenv("DJANGO_LOG_DIR", BASE_DIR / "logs"))
LOG_DIR.mkdir(exist_ok=True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")

DEBUG = _env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = _env_list(
    "DJANGO_ALLOWED_HOSTS",
    ["localhost", "127.0.0.1", "testserver"],
)
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "core",
    "users",
    "habits",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(os.getenv("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3")),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles"))

MEDIA_URL = os.getenv("DJANGO_MEDIA_URL", "/media/")
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.filebased.EmailBackend",
)

EMAIL_FILE_PATH = Path(os.getenv("DJANGO_EMAIL_FILE_PATH", BASE_DIR / "sent_emails"))

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in (
    "true",
    "1",
    "yes",
    "on",
)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "webmaster@localhost",
)
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "habit_list"
LOGOUT_REDIRECT_URL = "home"
AUTH_USER_MODEL = "users.CustomUser"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Habit Tracker API",
    "DESCRIPTION": "REST API for Habit Tracker project",
    "VERSION": "1.0.0",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "timed_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "daily.log"),
            "when": "midnight",
            "backupCount": 7,
            "encoding": "utf-8",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "rotating_file", "timed_file"],
            "level": "INFO",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "rotating_file", "timed_file"],
            "level": "INFO",
            "propagate": False,
        },
        "habits": {
            "handlers": ["console", "rotating_file", "timed_file"],
            "level": "INFO",
            "propagate": False,
        },
        "analytics": {
            "handlers": ["console", "rotating_file", "timed_file"],
            "level": "INFO",
            "propagate": False,
        },
        "api": {
            "handlers": ["console", "rotating_file", "timed_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
