"""
© Ocado Group
Created on 12/02/2025 at 16:48:47(+00:00).

This file contains custom settings defined by third party extensions.
"""

import os

from ..tasks import get_local_sqs_url as _get_local_sqs_url
from .custom import ENV, SERVICE_NAME, SERVICE_SITE_URL
from .django import TIME_ZONE
from .otp import AWS_REGION as OTP_AWS_REGION
from .otp import SQS_URL

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

# AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
# NOTE: These are set in the dev container:
# https://github.com/ocadotechnology/codeforlife-workspace/blob/main/.devcontainer/docker-compose.yml

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://aws:4566")

# Celery
# https://docs.celeryq.dev/en/v5.4.0/userguide/configuration.html
# https://docs.celeryq.dev/en/v5.4.0/getting-started/backends-and-brokers/sqs.html

CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = "sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": OTP_AWS_REGION if ENV != "local" else AWS_REGION,
    "predefined_queues": {
        SERVICE_NAME: {
            "url": (
                SQS_URL
                if ENV != "local"
                else _get_local_sqs_url(AWS_REGION, SERVICE_NAME)
            )
        }
    },
}
CELERY_TASK_DEFAULT_QUEUE = SERVICE_NAME
CELERY_TASK_TIME_LIMIT = 60 * 30
