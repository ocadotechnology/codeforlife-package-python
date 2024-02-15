"""
© Ocado Group
Created on 12/12/2023 at 13:55:22(+00:00).
"""

import typing as t

from ...permissions import IsAuthenticated
from ..models import User


class IsTeacher(IsAuthenticated):
    """Request's user must be a teacher."""

    def __init__(self, is_admin: t.Optional[bool] = None):
        """Initialize permission.

        Args:
            is_admin: If the teacher is an admin. If None, don't check if the
                teacher is an admin. Else, check if the teacher is (not) an
                admin.
        """

        super().__init__()
        self.is_admin = is_admin

    def __eq__(self, other):
        return super().__eq__(other) and self.is_admin == other.is_admin

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and user.student is None
            and user.teacher is not None
            and (
                self.is_admin is None or user.teacher.is_admin == self.is_admin
            )
        )
