"""
© Ocado Group
Created on 14/03/2024 at 12:14:54(+00:00).
"""

from django.db.models import signals

from ...models.signals import (
    UpdateFields,
    model_receiver,
    validate_update_fields_includes_none_or_all,
)
from ..models import User

user_receiver = model_receiver(User)

# pylint: disable=unused-argument,missing-function-docstring


@user_receiver(signals.pre_save)
def user__pre_save(
    sender,
    instance: User,
    raw: bool,
    using: str,
    update_fields: UpdateFields,
    **kwargs
):
    validate_update_fields_includes_none_or_all(
        update_fields, User.FIRST_NAME_FIELDS
    )
    validate_update_fields_includes_none_or_all(
        update_fields, User.EMAIL_FIELDS
    )
