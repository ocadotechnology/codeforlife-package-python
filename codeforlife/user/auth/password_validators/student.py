# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 30/01/2024 at 12:28:00(+00:00).
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .base import PasswordValidator


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class StudentPasswordValidator(PasswordValidator):
    def validate(self, password, user=None):
        # TODO: Remove third check once we switch to new models
        if user and user.student and user.student.class_field:
            min_length = 6

            if len(password) < min_length:
                raise ValidationError(
                    _(
                        f"Your password must be at least {min_length} "
                        f"characters long."
                    ),
                    code="password_too_short",
                )
