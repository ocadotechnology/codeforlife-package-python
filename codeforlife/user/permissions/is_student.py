"""
© Ocado Group
Created on 12/12/2023 at 13:55:40(+00:00).
"""

import typing as t

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import User


class IsStudent(BasePermission):
    """Request's user must be a student."""

    def __init__(self, student_id: t.Optional[int] = None):
        """Initialize permission.

        Args:
            student_id: A student's ID. If None, check if the user is any
                student. Else, check if the user is the specific student.
        """

        super().__init__()
        self.student_id = student_id

    def has_permission(self, request: Request, view: APIView):
        user = request.user
        return (
            isinstance(user, User)
            and user.student_id is not None
            and (self.student_id is None or user.student_id == self.student_id)
        )
