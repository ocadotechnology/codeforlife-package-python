# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 30/01/2024 at 12:32:00(+00:00).
"""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .base import PasswordValidator


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class TeacherPasswordValidator(PasswordValidator):
    def validate(self, password, user=None):
        if user and user.teacher:
            min_length = 10

            if len(password) < min_length:
                raise ValidationError(
                    _(
                        f"Your password needs to be at least {min_length} "
                        f"characters long."
                    ),
                    code="password_too_short",
                )

            if not re.search(r"[A-Z]", password):
                raise ValidationError(
                    _("Your password must have at least 1 uppercase letter."),
                    code="password_no_uppercase",
                )

            if not re.search(r"[a-z]", password):
                raise ValidationError(
                    _("Your password must have at least 1 lowercase letter."),
                    code="password_no_lowercase",
                )

            if not re.search(r"[0-9]", password):
                raise ValidationError(
                    _("Your password must have at least 1 digit."),
                    code="password_no_digit",
                )

            if not re.search(
                r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password
            ):
                raise ValidationError(
                    _("Your password must have at least 1 special character."),
                    code="password_no_special_character",
                )
