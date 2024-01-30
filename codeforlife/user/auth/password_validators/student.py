"""
© Ocado Group
Created on 30/01/2024 at 12:28:00(+00:00).
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .base import BasePasswordValidator


class StudentPasswordValidator(BasePasswordValidator):
    def __init__(self):
        self.min_length = 6

    def validate(self, password, user=None):
        if user.student is not None:
            if len(password) < self.min_length:
                raise ValidationError(
                    _(
                        f"Your password must be at least {self.min_length} "
                        f"characters long."
                    ),
                    code="password_too_short",
                )
