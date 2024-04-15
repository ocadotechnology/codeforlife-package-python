"""
© Ocado Group
Created on 12/04/2024 at 17:02:48(+01:00).
"""

from django.contrib.auth.backends import BaseBackend as _BaseBackend

from ...models import User


class BaseBackend(_BaseBackend):
    """Base backend which all other backend must inherit."""

    user_class = User

    def get_user(self, user_id: int):
        try:
            return self.user_class.objects.get(id=user_id)
        except self.user_class.DoesNotExist:
            return None
