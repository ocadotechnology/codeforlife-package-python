"""
© Ocado Group
Created on 23/07/2024 at 14:18:28(+01:00).
"""

from django.conf import settings
from django.contrib.sessions.middleware import (
    SessionMiddleware as _SessionMiddleware,
)


class SessionMiddleware(_SessionMiddleware):
    """
    Override the session middleware to delete the session metadata cookie when
    the session key cookie is deleted.
    """

    def process_response(self, request, response):
        response = super().process_response(request, response)

        session = response.cookies.get(settings.SESSION_COOKIE_NAME)
        if (
            session
            and session.get("max-age") == 0
            and session.get("expires") == "Thu, 01 Jan 1970 00:00:00 GMT"
        ):
            response.delete_cookie(
                key=settings.SESSION_METADATA_COOKIE_NAME,
                path=settings.SESSION_METADATA_COOKIE_PATH,
                domain=settings.SESSION_METADATA_COOKIE_DOMAIN,
                samesite=settings.SESSION_METADATA_COOKIE_SAMESITE,
            )

        return response
