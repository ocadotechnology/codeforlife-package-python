"""
© Ocado Group
Created on 12/02/2025 at 16:49:16(+00:00).

This file contains all of our custom settings we define for our own purposes.
"""

import json
import os
import re
import typing as t
from pathlib import Path

import boto3

from .otp import (
    AWS_S3_APP_BUCKET,
    AWS_S3_APP_FOLDER,
    AWS_S3_STATIC_FOLDER,
    CACHE_DB_DATA_PATH,
)

if t.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

    from ..server import Server
    from ..types import CookieSamesite, DatabaseEngine, Env, JsonDict


# The name of the current environment.
ENV = t.cast("Env", os.getenv("ENV", "local"))

# The database's engine type.
DB_ENGINE = t.cast("DatabaseEngine", os.getenv("DB_ENGINE", "postgresql"))

# The mode the service is being served in.
SERVER_MODE = t.cast("Server.Mode", os.getenv("SERVER_MODE", "django"))

# The level of the logs.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# The base directory of the current service.
SERVICE_BASE_DIR = Path(os.getenv("SERVICE_BASE_DIR", "/"))

# The name of the current service.
SERVICE_NAME = os.getenv("SERVICE_NAME", "REPLACE_ME")

# The protocol, domain and port of the current service.
SERVICE_PROTOCOL = os.getenv("SERVICE_PROTOCOL", "http")
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN", "localhost")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

# The host and base url of the current service.
SERVICE_HOST = f"{SERVICE_DOMAIN}:{SERVICE_PORT}"
SERVICE_BASE_URL = f"{SERVICE_PROTOCOL}://{SERVICE_HOST}"

# The domain without the last level and a preceding dot.
# If the domain does not contain multiple levels, then it remains the same.
# Examples:
#   - domain: "www.example.com" -> external domain: ".example.com".
#   - domain: "localhost" -> external domain: "localhost".
SERVICE_EXTERNAL_DOMAIN = (
    t.cast(re.Match, re.match(r".+?(\..+)", SERVICE_DOMAIN)).group(1)
    if "." in SERVICE_DOMAIN
    else SERVICE_DOMAIN
)

# The frontend url of the current service.
SERVICE_SITE_URL = os.getenv("SERVICE_SITE_URL", "http://localhost:5173")

# The location of the service's folder in the s3 buckets.
SERVICE_S3_APP_LOCATION = f"{AWS_S3_APP_FOLDER}/{SERVICE_NAME}/{SERVER_MODE}"
SERVICE_S3_STATIC_LOCATION = (
    f"{AWS_S3_STATIC_FOLDER}/{SERVICE_NAME}/{SERVER_MODE}"
)

# The authorization bearer token used to authenticate with Dotdigital.
MAIL_AUTH = os.getenv("MAIL_AUTH", "REPLACE_ME")

# A global flag to enable/disable sending emails.
# If disabled, emails will be logged to the console instead.
MAIL_ENABLED = bool(int(os.getenv("MAIL_ENABLED", "0")))

# The session metadata cookie settings.
# These work the same as Django's session cookie settings.
SESSION_METADATA_COOKIE_NAME = "session_metadata"
SESSION_METADATA_COOKIE_PATH = "/"
SESSION_METADATA_COOKIE_DOMAIN = SERVICE_EXTERNAL_DOMAIN
SESSION_METADATA_COOKIE_SAMESITE: "CookieSamesite" = "Strict"


def get_redis_url():
    """Get the Redis URL for the current environment.

    Raises:
        ConnectionAbortedError: If the engine is not Redis.

    Returns:
        The Redis URL.
    """

    if ENV == "local":
        host = os.getenv("REDIS_HOST", "cache")
        port = int(os.getenv("REDIS_PORT", "6379"))
        path = os.getenv("REDIS_PATH", "0")
        url = f"{host}:{port}/{path}"
    else:
        # Get the dbdata object.
        s3: "S3Client" = boto3.client("s3")
        db_data_object = s3.get_object(
            Bucket=t.cast(str, AWS_S3_APP_BUCKET), Key=CACHE_DB_DATA_PATH
        )

        # Load the object as a JSON dict.
        db_data: "JsonDict" = json.loads(
            db_data_object["Body"].read().decode("utf-8")
        )
        if not db_data or db_data["Engine"] != "Redis":
            raise ConnectionAbortedError("Invalid database data.")

        endpoint = t.cast(dict, db_data["Endpoint"])
        url = t.cast(str, endpoint["0001"])

    return f"redis://{url}"


# The URL to connect to the Redis cache.
REDIS_URL = get_redis_url()
