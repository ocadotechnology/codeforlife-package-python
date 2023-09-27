import typing as t

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser

from ....request import WSGIRequest
from ...models import User


class UsernameAndPasswordAndClassIdBackend(BaseBackend):
    def authenticate(
        self,
        request: WSGIRequest,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        class_id: t.Optional[str] = None,
        **kwargs
    ) -> t.Optional[AbstractBaseUser]:
        if username is None or password is None or class_id is None:
            return

        try:
            user = User.objects.get(
                username=username,
                new_student__class_field__access_code=class_id,
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return

    def get_user(self, user_id: int) -> t.Optional[AbstractBaseUser]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
