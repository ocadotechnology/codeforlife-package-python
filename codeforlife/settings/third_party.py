"""
This file contains custom settings defined by third party extensions.
"""

import json
import os

from .custom import SERVICE_SITE_URL
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
}

# Django storages
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_OBJECT_PARAMETERS = json.loads(
    os.getenv("AWS_S3_OBJECT_PARAMETERS", "{}")
)
AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL")
AWS_QUERYSTRING_AUTH = bool(int(os.getenv("AWS_QUERYSTRING_AUTH", "1")))
AWS_S3_MAX_MEMORY_SIZE = int(os.getenv("AWS_S3_MAX_MEMORY_SIZE", "0"))
AWS_QUERYSTRING_EXPIRE = int(os.getenv("AWS_QUERYSTRING_EXPIRE", "3600"))
AWS_S3_URL_PROTOCOL = os.getenv("AWS_S3_URL_PROTOCOL", "https:")
AWS_S3_FILE_OVERWRITE = bool(int(os.getenv("AWS_S3_FILE_OVERWRITE", "1")))
AWS_LOCATION = os.getenv("AWS_LOCATION", "")
AWS_IS_GZIPPED = bool(int(os.getenv("AWS_IS_GZIPPED", "0")))
GZIP_CONTENT_TYPES = os.getenv(
    "GZIP_CONTENT_TYPES",
    "("
    + ",".join(
        [
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/x-javascript",
            "image/svg+xml",
        ]
    )
    + ")",
)
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_USE_SSL = bool(int(os.getenv("AWS_S3_USE_SSL", "1")))
AWS_S3_VERIFY = os.getenv("AWS_S3_VERIFY")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE")
AWS_S3_PROXIES = os.getenv("AWS_S3_PROXIES")
AWS_S3_TRANSFER_CONFIG = os.getenv("AWS_S3_TRANSFER_CONFIG")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_CLOUDFRONT_KEY = os.getenv("AWS_CLOUDFRONT_KEY")
AWS_CLOUDFRONT_KEY_ID = os.getenv("AWS_CLOUDFRONT_KEY_ID")
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION")
AWS_S3_CLIENT_CONFIG = os.getenv("AWS_S3_CLIENT_CONFIG")
