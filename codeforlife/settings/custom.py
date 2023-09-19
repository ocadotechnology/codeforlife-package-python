"""
This file contains all of our custom settings we define for our own purposes.
"""

import os

# The name of the current service.
SERVICE_NAME = os.environ["SERVICE_NAME"]  # *required

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
