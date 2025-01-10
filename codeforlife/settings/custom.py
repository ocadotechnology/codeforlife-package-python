"""
This file contains all of our custom settings we define for our own purposes.
"""

import os
import typing as t
from pathlib import Path

from ..types import CookieSamesite, Env

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

# The frontend url of the current service.
SERVICE_SITE_URL = os.getenv("SERVICE_SITE_URL", "http://localhost:5173")

# The authorization bearer token used to authenticate with Dotdigital.
MAIL_AUTH = os.getenv("MAIL_AUTH", "REPLACE_ME")

# A global flag to enable/disable sending emails.
# If disabled, emails will be logged to the console instead.
MAIL_ENABLED = bool(int(os.getenv("MAIL_ENABLED", "0")))

# The session metadata cookie settings.
# These work the same as Django's session cookie settings.
SESSION_METADATA_COOKIE_NAME = "session_metadata"
SESSION_METADATA_COOKIE_PATH = "/"
SESSION_METADATA_COOKIE_DOMAIN = os.getenv(
    "SESSION_METADATA_COOKIE_DOMAIN", "localhost"
)
SESSION_METADATA_COOKIE_SAMESITE: CookieSamesite = "Strict"
