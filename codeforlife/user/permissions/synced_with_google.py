"""
© Ocado Group
Created on 02/09/2025 at 10:48:07(+01:00).
"""

from ...permissions import IsAuthenticated
from ..models import GoogleUser, User


class SyncedWithGoogle(IsAuthenticated):
    """Request's user must be synced with Google."""

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and GoogleUser.objects.filter(id=user.id).exists()
        )
