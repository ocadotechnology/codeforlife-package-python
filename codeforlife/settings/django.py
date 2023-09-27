"""
This file contains all of the settings Django supports out of the box.
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os

from django.utils.translation import gettext_lazy as _

from .custom import SERVICE_API_URL, SERVICE_NAME

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", "1")))

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
    "codeforlife.user.auth.backends.UserIdAndLoginIdBackend",
    "codeforlife.user.auth.backends.UsernameAndPasswordAndClassIdBackend",
]

# Sessions
# https://docs.djangoproject.com/en/3.2/topics/http/sessions/

SESSION_ENGINE = "codeforlife.user.models.session"
SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_DOMAIN = "localhost" if DEBUG else "codeforlife.education"

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"
LANGUAGES = [("en-gb", _("English"))]
TIME_ZONE = "Europe/London"  # TODO: use UTC?
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"  # TODO: use BigAutoField

# CSRF
# https://docs.djangoproject.com/en/3.2/ref/csrf/

CSRF_COOKIE_NAME = f"{SERVICE_NAME}_csrftoken"
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

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
# https://docs.djangoproject.com/en/4.2/ref/settings/#root-urlconf

ROOT_URLCONF = "service.urls"

# App
# https://docs.djangoproject.com/en/4.2/ref/settings/#wsgi-application

WSGI_APPLICATION = "service.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

# TODO: replace with custom validators:
# 1. codeforlife.user.auth.password_validators.TeacherPasswordValidator
# 2. codeforlife.user.auth.password_validators.DependentStudentPasswordValidator
# 3. codeforlife.user.auth.password_validators.IndependentStudentPasswordValidator
# 4. codeforlife.user.auth.password_validators.CommonPasswordValidator
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
