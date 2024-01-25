"""
© Ocado Group
Created on 12/12/2023 at 15:18:10(+00:00).
"""

import typing as t

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from ..models import User


class InClass(IsAuthenticated):
    """Request's user must be in a class."""

    def __init__(self, class_id: t.Optional[str] = None):
        """Initialize permission.

        Args:
            class_id: A class' ID. If None, check if user is in any class.
                Else, check if user is in the specific class.
        """

        super().__init__()
        self.class_id = class_id

    def has_permission(self, request: Request, view: APIView):
        user = request.user
        if super().has_permission(request, view) and isinstance(user, User):
            if user.teacher is not None:
                classes = user.teacher.class_teacher
                if self.class_id is not None:
                    classes = classes.filter(access_code=self.class_id)
                return classes.exists()

            if user.student is not None:
                if self.class_id is None:
                    return True
                return (
                    user.student.class_field is not None
                    and user.student.class_field.access_code == self.class_id
                )

        return False
