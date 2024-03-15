"""
© Ocado Group
Created on 15/03/2024 at 14:47:03(+00:00).
"""

from rest_framework.permissions import AllowAny as _AllowAny

from .base import BasePermission


class AllowAny(BasePermission, _AllowAny):
    """Allows all incoming requests."""
