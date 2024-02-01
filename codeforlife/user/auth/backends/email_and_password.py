"""
© Ocado Group
Created on 01/02/2024 at 14:34:04(+00:00).
"""

import typing as t

from django.contrib.auth.backends import BaseBackend

from ....request import HttpRequest
from ...models import User


class EmailAndPasswordBackend(BaseBackend):
    """Authenticate a user by checking their email and password."""

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **kwargs
    ):
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email__iexact=email)
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
