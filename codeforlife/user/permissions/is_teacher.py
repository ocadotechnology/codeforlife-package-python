"""
© Ocado Group
Created on 12/12/2023 at 13:55:22(+00:00).
"""

import typing as t

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import User


class IsTeacher(BasePermission):
    """Request's user must be a teacher."""

    def __init__(self, teacher_id: t.Optional[int] = None):
        """Initialize permission.

        Args:
            teacher_id: A teacher's ID. If passed, the user must be this
                teacher.
        """

        super().__init__()
        self.teacher_id = teacher_id

    def has_permission(self, request: Request, view: APIView):
        user = request.user
        return (
            isinstance(user, User)
            and user.teacher_id is not None
            and (self.teacher_id is None or user.teacher_id == self.teacher_id)
        )
