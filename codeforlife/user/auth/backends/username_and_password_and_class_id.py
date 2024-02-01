"""
© Ocado Group
Created on 01/02/2024 at 14:48:17(+00:00).
"""

import typing as t

from django.contrib.auth.backends import BaseBackend

from ....request import HttpRequest
from ...models import User


class UsernameAndPasswordAndClassIdBackend(BaseBackend):
    """Authenticate a student using their username, password and class ID."""

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        class_id: t.Optional[str] = None,
        **kwargs
    ):
        if username is None or password is None or class_id is None:
            return None

        try:
            user = User.objects.get(
                username=username,
                new_student__class_field__access_code=class_id,
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        return None

    def get_user(self, user_id: int):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
