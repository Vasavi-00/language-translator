"""
Django settings for translator_project.

Every section below is commented so a beginner can follow along.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from a .env file (if present) into the environment.
# This means SECRET_KEY, DEBUG, etc. can be kept out of source control.
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------

# SECRET_KEY is used by Django for cryptographic signing (sessions, CSRF, etc.)
# NEVER hard-code a real secret key in production. It is read from .env.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-only-key-change-me-in-production"
)

# DEBUG=True shows detailed error pages. MUST be False in production.
DEBUG = os.getenv("DEBUG", "True") == "True"

# List of host/domain names this Django site can serve.
# In production this should be your real domain, e.g. "mytranslator.onrender.com"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# ------------------------------------------------------------------
# APPLICATION DEFINITION
# ------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "corsheaders",

    # Local apps
    "translator_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files efficiently in production (right after Security).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS middleware must be placed as high as possible, above CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "translator_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates directory (in addition to each app's templates/ folder)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "translator_project.wsgi.application"
ASGI_APPLICATION = "translator_project.asgi.application"

# ------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------
# SQLite is used for simplicity. Swap this for PostgreSQL in production
# by setting a DATABASE_URL and using dj-database-url if desired.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------------------------

STATIC_URL = "static/"
# Extra locations Django looks in for static files during development.
STATICFILES_DIRS = [BASE_DIR / "static"]
# Where `collectstatic` gathers everything for production.
STATIC_ROOT = BASE_DIR / "staticfiles"
# WhiteNoise: compress and add cache-busting hashes to static file names.
# The "Manifest" storage requires `collectstatic` to have been run (it looks
# up a manifest file), so it's only used in production (DEBUG=False). In
# development we use the plain compressed storage so `runserver` and tests
# work immediately without an extra build step.
if DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
# ------------------------------------------------------------------
# Needed if the frontend is ever served from a different domain/port
# than the Django backend (e.g. a separate React app).

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]

# ------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
    },
}

# ------------------------------------------------------------------
# TRANSLATION SETTINGS (custom, used by translator_app/services.py)
# ------------------------------------------------------------------

TRANSLATION_ENGINE = os.getenv("TRANSLATION_ENGINE", "google")  # "google" or "libre"
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com/translate")
LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "")

# ------------------------------------------------------------------
# PRODUCTION SECURITY HARDENING
# ------------------------------------------------------------------
# These only take effect when DEBUG=False, so local development is unaffected.

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
