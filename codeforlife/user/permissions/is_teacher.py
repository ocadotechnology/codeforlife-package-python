# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 12/12/2023 at 13:55:22(+00:00).
"""

import typing as t

from ...permissions import IsAuthenticated
from ..models import User


class IsTeacher(IsAuthenticated):
    """Request's user must be a teacher."""

    def __init__(
        self,
        is_admin: t.Optional[bool] = None,
        in_school: t.Optional[bool] = None,
        in_class: t.Optional[bool] = None,
    ):
        # pylint: disable=line-too-long
        """Initialize permission.

        Args:
            is_admin: Check if the teacher is (not) an admin. If None, don't check. If True, in_school is set to True.
            in_school: Check if the teacher is (not) in a school. If None, don't check.
            in_class: Check if the teacher is (not) in a class. If None, don't check. If True, in_school is set to True.
        """
        # pylint: enable=line-too-long
        super().__init__()

        if is_admin or in_class:
            in_school = True

        self.is_admin = is_admin
        self.in_school = in_school
        self.in_class = in_class

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.is_admin == other.is_admin
            and self.in_school == other.in_school
            and self.in_class == other.in_class
        )

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and user.student is None
            and user.teacher is not None
            and (
                self.in_school is None
                or (self.in_school and user.teacher.school_id is not None)
                or (not self.in_school and user.teacher.school_id is None)
            )
            and (
                self.is_admin is None or user.teacher.is_admin == self.is_admin
            )
            and (
                self.in_class is None
                or (self.in_class and user.teacher.class_teacher.exists())
                or (
                    not self.in_class
                    and not user.teacher.class_teacher.exists()
                )
            )
        )
