# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 12/12/2023 at 13:55:40(+00:00).
"""

from ...permissions import IsAuthenticated
from ..models import User


class IsStudent(IsAuthenticated):
    """Request's user must be a student."""

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and user.teacher is None
            and user.student is not None
            and user.student.class_field is not None
            and user.student.class_field.teacher.school_id is not None
        )
