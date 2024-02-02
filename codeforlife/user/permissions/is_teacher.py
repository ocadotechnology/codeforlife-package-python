"""
© Ocado Group
Created on 12/12/2023 at 13:55:22(+00:00).
"""

import typing as t

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import User


class IsTeacher(IsAuthenticated):
    """Request's user must be a teacher."""

    def __init__(
        self,
        teacher_id: t.Optional[int] = None,
        is_admin: t.Optional[bool] = None,
    ):
        """Initialize permission.

        Args:
            teacher_id: A teacher's ID. If None, check if the user is any
                teacher. Else, check if the user is the specific teacher.
            is_admin: If the teacher is an admin. If None, don't check if the
                teacher is an admin. Else, check if the teacher is (not) an
                admin.
        """

        super().__init__()
        self.teacher_id = teacher_id
        self.is_admin = is_admin

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.teacher_id == other.teacher_id
            and self.is_admin == other.is_admin
        )

    def has_permission(self, request: Request, view: APIView):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and user.teacher is not None
            and (self.teacher_id is None or user.teacher.id == self.teacher_id)
            and (
                self.is_admin is None or user.teacher.is_admin == self.is_admin
            )
        )
