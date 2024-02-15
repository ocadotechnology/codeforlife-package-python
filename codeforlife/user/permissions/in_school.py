"""
© Ocado Group
Created on 12/12/2023 at 15:18:27(+00:00).
"""

from ...permissions import IsAuthenticated
from ..models import User


class InSchool(IsAuthenticated):
    """Request's user must be in a school."""

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and (
                (
                    user.teacher is not None
                    and user.teacher.school_id is not None
                )
                or (
                    user.student is not None
                    and user.student.class_field is not None
                    and user.student.class_field.teacher.school_id is not None
                )
            )
        )
