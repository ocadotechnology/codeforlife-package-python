import typing as t

from django.contrib.auth.backends import BaseBackend
from django.http.request import HttpRequest

from ...models import User


class EmailAndPasswordBackend(BaseBackend):
    """Authenticates if the password belongs to the anon user's email."""

    def authenticate(
        self,
        request: t.Optional[HttpRequest],
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **kwargs
    ):
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email)
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
