"""
© Ocado Group
Created on 12/12/2023 at 13:55:47(+00:00).
"""

from rest_framework.permissions import IsAuthenticated

from ..models import User


class IsIndependent(IsAuthenticated):
    """Request's user must be independent."""

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and user.teacher is None
            and user.student is not None
            and user.student.class_field is None
        )
