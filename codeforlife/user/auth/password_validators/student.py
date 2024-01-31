"""
© Ocado Group
Created on 30/01/2024 at 12:28:00(+00:00).
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .base import PasswordValidator


class StudentPasswordValidator(PasswordValidator):

    def validate(self, password, user=None):
        if user.student is not None:
            min_length = 6

            if len(password) < min_length:
                raise ValidationError(
                    _(
                        f"Your password must be at least {min_length} "
                        f"characters long."
                    ),
                    code="password_too_short",
                )
