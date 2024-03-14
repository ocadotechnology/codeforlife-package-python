"""
© Ocado Group
Created on 14/03/2024 at 12:14:54(+00:00).
"""

# TODO: use custom User model in new data schema
# from ..models import User
# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import User

from ...models.signals import model_receiver

user_receiver = model_receiver(User)
