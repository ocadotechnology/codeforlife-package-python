"""
© Ocado Group
Created on 02/01/2025 at 12:11:50(+00:00).
"""

import json
from logging import Formatter

from django.conf import settings


class JsonFormatter(Formatter):
    """Format message as a stringified JSON object."""

    def format(self, record):
        message = super().format(record)

        return json.dumps(
            {
                "serviceName": settings.SERVICE_NAME,
                "name": record.name,
                "level": record.levelname,
                "message": message,
            },
            separators=(",", ":"),
        )
