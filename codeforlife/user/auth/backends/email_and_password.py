import typing as t

from django.contrib.auth.backends import BaseBackend

from ....request import WSGIRequest
from ...models import User


class EmailAndPasswordBackend(BaseBackend):
    def authenticate(
        self,
        request: WSGIRequest,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **kwargs
    ):
        if email is None or password is None:
            return

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return

    def get_user(self, user_id: int):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
