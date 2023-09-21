import typing as t

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.handlers.wsgi import WSGIRequest

User = get_user_model()


class EmailAndPasswordBackend(BaseBackend):
    def authenticate(
        self,
        request: WSGIRequest,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **kwargs
    ) -> t.Optional[AbstractBaseUser]:
        if email is None or password is None:
            return

        try:
            user = User.objects.get(email=email)
            if getattr(user, "is_active", True) and user.check_password(
                password
            ):
                return user
        except User.DoesNotExist:
            return

    def get_user(self, user_id: int) -> t.Optional[AbstractBaseUser]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
