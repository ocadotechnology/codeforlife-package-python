"""
© Ocado Group
Created on 23/01/2024 at 14:46:23(+00:00).
"""

from rest_framework.permissions import BasePermission


class AllowNone(BasePermission):
    """
    Blocks all incoming requests.

    This is the opposite of DRF's AllowAny permission:
    https://www.django-rest-framework.org/api-guide/permissions/#allowany
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def has_permission(self, request, view):
        return False
