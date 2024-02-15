"""
© Ocado Group
Created on 23/01/2024 at 14:46:23(+00:00).
"""

from .base import BasePermission


class AllowNone(BasePermission):
    """
    Blocks all incoming requests.

    This is the opposite of DRF's AllowAny permission:
    https://www.django-rest-framework.org/api-guide/permissions/#allowany
    """

    def has_permission(self, request, view):
        return False
