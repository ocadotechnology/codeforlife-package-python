"""
© Ocado Group
Created on 01/02/2024 at 14:44:16(+00:00).
"""

import typing as t

from common.helpers.generators import get_hashed_login_id
from django.contrib.auth.backends import BaseBackend

from ....request import HttpRequest
from ...models import Student, StudentUser


class UserIdAndLoginIdBackend(BaseBackend):
    """Authenticate a student using their ID and auto-generated password."""

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        user_id: t.Optional[int] = None,
        login_id: t.Optional[str] = None,
        **kwargs
    ):
        if user_id is None or login_id is None:
            return None

        user = self.get_user(user_id)
        if user:
            # Check the url against the student's stored hash.
            student = Student.objects.get(new_user=user)
            if (
                student.login_id
                # TODO: refactor this
                and get_hashed_login_id(login_id) == student.login_id
            ):
                return user

        return None

    def get_user(self, user_id: int):
        try:
            return StudentUser.objects.get(id=user_id)
        except StudentUser.DoesNotExist:
            return None
