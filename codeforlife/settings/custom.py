"""
© Ocado Group
Created on 12/02/2025 at 16:49:16(+00:00).

This file contains all of our custom settings we define for our own purposes.
"""

import os
import re
import typing as t
from pathlib import Path

from ..types import CookieSamesite, Env
from .otp import AWS_S3_APP_FOLDER, AWS_S3_STATIC_FOLDER

# The name of the current environment.
ENV = t.cast(Env, os.getenv("ENV", "local"))

# The base directory of the current service.
SERVICE_BASE_DIR = Path(os.getenv("SERVICE_BASE_DIR", "/"))

# The name of the current service.
SERVICE_NAME = os.getenv("SERVICE_NAME", "REPLACE_ME")

# The protocol, domain and port of the current service.
SERVICE_PROTOCOL = os.getenv("SERVICE_PROTOCOL", "http")
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN", "localhost")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

# The base url of the current service.
# The root service does not need its name included in the base url.
SERVICE_BASE_URL = f"{SERVICE_PROTOCOL}://{SERVICE_DOMAIN}:{SERVICE_PORT}"

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
SERVICE_S3_APP_LOCATION = f"{AWS_S3_APP_FOLDER}/{SERVICE_NAME}"
SERVICE_S3_STATIC_LOCATION = f"{AWS_S3_STATIC_FOLDER}/{SERVICE_NAME}"

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
SESSION_METADATA_COOKIE_SAMESITE: CookieSamesite = "Strict"
