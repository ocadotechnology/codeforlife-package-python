import typing as t

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser

from ....request import WSGIRequest
from ...models import User


class EmailAndTokenBackend(BaseBackend):
    def authenticate(
        self,
        request: WSGIRequest,
        email: t.Optional[str] = None,
        token: t.Optional[str] = None,
        **kwargs,
    ) -> t.Optional[AbstractBaseUser]:
        if email is None or token is None:
            return

        try:
            user = User.objects.get(email=email)
            if any(
                backup_token.check_token(token)
                for backup_token in user.backup_tokens
            ):
                return user
        except User.DoesNotExist:
            return

    def get_user(self, user_id: int) -> t.Optional[AbstractBaseUser]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
