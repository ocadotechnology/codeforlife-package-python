"""
This file contains all the settings Django supports out of the box.
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os

from django.utils.translation import gettext_lazy as _

from .custom import SERVICE_API_URL, SERVICE_NAME

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", "1")))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

ALLOWED_HOSTS = ["*"]

# Application definition

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
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
    "codeforlife.user.auth.backends.EmailAndPasswordBackend",
    "codeforlife.user.auth.backends.OtpBackend",
    "codeforlife.user.auth.backends.OtpBypassTokenBackend",
    "codeforlife.user.auth.backends.UserIdAndLoginIdBackend",
    "codeforlife.user.auth.backends.FirstNameAndPasswordAndClassIdBackend",
]

# Sessions
# https://docs.djangoproject.com/en/3.2/topics/http/sessions/

SESSION_ENGINE = "codeforlife.user.models.session"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = "sessionid_httponly_true"
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

ROOT_URLCONF = "service.urls"

# App
# https://docs.djangoproject.com/en/3.2/ref/settings/#wsgi-application

WSGI_APPLICATION = "service.wsgi.application"

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
    "codeforlife.user",
    "corsheaders",
    "rest_framework",
    "django_filters",
]
