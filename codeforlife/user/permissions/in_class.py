"""
© Ocado Group
Created on 12/12/2023 at 15:18:10(+00:00).
"""

from rest_framework.permissions import IsAuthenticated

from ..models import User


class InClass(IsAuthenticated):
    """Request's user must be in a class."""

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def has_permission(self, request, view):
        user = request.user
        if super().has_permission(request, view) and isinstance(user, User):
            if user.teacher is not None:
                return user.teacher.class_teacher.exists()
            if user.student is not None:
                return user.student.class_field is not None

        return False
