"""
© Ocado Group
Created on 12/02/2025 at 16:48:47(+00:00).

This file contains custom settings defined by third party extensions.
"""

import typing as t

from ..tasks import CeleryBeat
from .custom import REDIS_URL, SERVICE_SITE_URL
from .django import ENV

# CORS
# https://pypi.org/project/django-cors-headers/

CORS_ALLOW_ALL_ORIGINS = ENV == "local"
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [SERVICE_SITE_URL]

# REST framework
# https://www.django-rest-framework.org/api-guide/settings/#settings

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "codeforlife.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_PAGINATION_CLASS": "codeforlife.pagination.LimitOffsetPagination",
    "NON_FIELD_ERRORS_KEY": "__all__",
}

# Celery
# https://docs.celeryq.dev/en/v5.4.0/userguide/configuration.html

CELERY_BROKER_URL = REDIS_URL
CELERY_TASK_TIME_LIMIT = 60 * 30
CELERY_BEAT_SCHEDULE: t.Dict[str, t.Dict[str, CeleryBeat]] = {}
