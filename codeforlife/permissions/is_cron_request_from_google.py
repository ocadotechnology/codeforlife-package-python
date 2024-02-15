"""
© Ocado Group
Created on 23/01/2024 at 14:45:07(+00:00).
"""

from django.conf import settings

from .base import BasePermission


class IsCronRequestFromGoogle(BasePermission):
    """
    Validate that requests to your cron URLs are coming from App Engine and not
    from another source.
    https://cloud.google.com/appengine/docs/flexible/scheduling-jobs-with-cron-yaml#securing_urls_for_cron
    """

    def has_permission(self, request, view):
        return (
            settings.DEBUG
            or request.META.get("HTTP_X_APPENGINE_CRON") == "true"
        )
