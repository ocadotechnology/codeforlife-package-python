"""
© Ocado Group
Created on 12/02/2025 at 16:48:47(+00:00).

This file contains custom settings defined by third party extensions.
"""

import os
import typing as t

from .custom import SERVICE_NAME, SERVICE_SITE_URL
from .django import ENV
from .otp import AWS_REGION, SQS_URL

if t.TYPE_CHECKING:
    from ..tasks import CeleryBeatSchedule


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
# https://docs.celeryq.dev/en/v5.4.0/getting-started/backends-and-brokers/sqs.html

CELERY_BROKER_URL = "sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": AWS_REGION if ENV != "local" else os.environ["AWS_REGION"],
    "predefined_queues": {
        SERVICE_NAME: {
            "url": (
                SQS_URL
                if ENV != "local"
                else (
                    "http://sqs.us-east-1.localhost.localstack.cloud:4566"
                    f"/000000000000/{SERVICE_NAME}"
                )
            )
        }
    },
}
CELERY_TASK_DEFAULT_QUEUE = SERVICE_NAME
CELERY_TASK_TIME_LIMIT = 60 * 30
