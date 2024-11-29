"""
This file contains all of our custom settings we define for our own purposes.
"""

import os

# The name of the current service.
SERVICE_NAME = os.getenv("SERVICE_NAME", "REPLACE_ME")

# If the current service the root service. This will only be true for portal.
SERVICE_IS_ROOT = bool(int(os.getenv("SERVICE_IS_ROOT", "0")))

# The protocol, domain and port of the current service.
SERVICE_PROTOCOL = os.getenv("SERVICE_PROTOCOL", "http")
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN", "localhost")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

# The base url of the current service.
# The root service does not need its name included in the base url.
SERVICE_BASE_URL = f"{SERVICE_PROTOCOL}://{SERVICE_DOMAIN}:{SERVICE_PORT}"
if not SERVICE_IS_ROOT:
    SERVICE_BASE_URL += f"/{SERVICE_NAME}"

# The api url of the current service.
SERVICE_API_URL = f"{SERVICE_BASE_URL}/api"

# The website url of the current service.
SERVICE_SITE_URL = (
    "http://localhost:5173"
    if SERVICE_DOMAIN == "localhost"
    else SERVICE_BASE_URL
)

# The authorization bearer token used to authenticate with Dotdigital.
MAIL_AUTH = os.getenv("MAIL_AUTH", "REPLACE_ME")

# A global flag to enable/disable sending emails.
# If disabled, emails will be logged to the console instead.
MAIL_ENABLED = bool(int(os.getenv("MAIL_ENABLED", "0")))

# The name of the session metadata cookie.
SESSION_METADATA_COOKIE_NAME = "session_metadata"
