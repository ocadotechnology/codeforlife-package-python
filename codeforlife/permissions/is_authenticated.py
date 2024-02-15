"""
© Ocado Group
Created on 15/02/2024 at 15:54:39(+00:00).
"""

from rest_framework.permissions import IsAuthenticated as _IsAuthenticated

from .base import BasePermission


class IsAuthenticated(BasePermission, _IsAuthenticated):
    """Checks the incoming request is being made by an authenticated user."""
