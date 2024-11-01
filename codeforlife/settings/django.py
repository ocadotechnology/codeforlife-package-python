"""
This file contains all the settings Django supports out of the box.
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

from .custom import SERVICE_API_URL, SERVICE_NAME

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", "1")))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", SERVICE_NAME),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": int(os.getenv("DB_PORT", "5432")),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password"),
        "ATOMIC_REQUESTS": True,
    }
}

# Application definition

MIDDLEWARE = [
    "codeforlife.middlewares.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # Required to use the admin app.
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "replace-me")

# Auth
# https://docs.djangoproject.com/en/3.2/topics/auth/default/

LOGIN_URL = f"{SERVICE_API_URL}/session/expired/"

# Authentication backends
# https://docs.djangoproject.com/en/3.2/ref/settings/#authentication-backends

AUTHENTICATION_BACKENDS = [
    "codeforlife.user.auth.backends.EmailBackend",
    "codeforlife.user.auth.backends.OtpBackend",
    "codeforlife.user.auth.backends.OtpBypassTokenBackend",
    "codeforlife.user.auth.backends.StudentBackend",
    "codeforlife.user.auth.backends.StudentAutoBackend",
]

# Sessions
# https://docs.djangoproject.com/en/3.2/topics/http/sessions/

SESSION_ENGINE = "codeforlife.user.models.session"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = "session_key"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_DOMAIN = "localhost" if DEBUG else "codeforlife.education"

# Security
# https://docs.djangoproject.com/en/3.2/topics/security/

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"
LANGUAGES = [("en-gb", _("English"))]
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# CSRF
# https://docs.djangoproject.com/en/3.2/ref/csrf/

# TODO: Decide on CSRF approach
CSRF_COOKIE_NAME = f"{SERVICE_NAME}_csrftoken"
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
# CSRF_USE_SESSION = True

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
            "style": "%",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "handlers": ["console"],
    },
}

# URLs
# https://docs.djangoproject.com/en/3.2/ref/settings/#root-urlconf

ROOT_URLCONF = "api.urls"

# App
# https://docs.djangoproject.com/en/3.2/ref/settings/#wsgi-application

WSGI_APPLICATION = "application.app"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

# TODO: compare Django's default common password validator with our own and
#  decide which to keep
# NOTE: Django's common password validator, while similar to ours,
# seems based on a deprecated list of passwords.
# codeforlife.user.auth.password_validators.CommonPasswordValidator
# pylint: disable=line-too-long
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "codeforlife.user.auth.password_validators.TeacherPasswordValidator",
    },
    {
        "NAME": "codeforlife.user.auth.password_validators.StudentPasswordValidator",
    },
    {
        "NAME": "codeforlife.user.auth.password_validators.IndependentPasswordValidator",
    },
]
# pylint: enable=line-too-long

# Installed Apps
# https://docs.djangoproject.com/en/3.2/ref/settings/#installed-apps

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "game",  # TODO: remove
    "portal",  # TODO: remove
    "common",  # TODO: remove
    "api",
    "codeforlife.user",
    "corsheaders",
    "rest_framework",
    "django_filters",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


def get_static_root(base_dir: Path):
    """Get the static root for the Django project.

    Args:
        base_dir: The base directory of the Django project.

    Returns:
        The static root for the django project.
    """
    return base_dir / "static"


STATIC_URL = "/static/"

# Templates
# https://docs.djangoproject.com/en/3.2/ref/templates/

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
