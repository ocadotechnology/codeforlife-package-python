"""
© Ocado Group
Created on 12/12/2023 at 15:18:27(+00:00).
"""

import typing as t

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import User


class InSchool(BasePermission):
    """Request's user must be in a school."""

    def __init__(self, school_id: t.Optional[int] = None):
        """Initialize permission.

        Args:
            school_id: A school's ID. If None, check if user is in any school.
                Else, check if user is in the specific school.
        """

        super().__init__()
        self.school_id = school_id

    def has_permission(self, request: Request, view: APIView):
        def in_school(school_id: int):
            return self.school_id is None or self.school_id == school_id

        user = request.user
        return isinstance(user, User) and (
            (
                user.teacher is not None
                and user.teacher.school_id is not None
                and in_school(user.teacher.school_id)
            )
            or (user.student is not None and in_school(user.student.school_id))
        )
