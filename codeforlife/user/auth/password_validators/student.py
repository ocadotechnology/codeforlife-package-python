"""
© Ocado Group
Created on 30/01/2024 at 12:28:00(+00:00).
"""

from django.core.exceptions import ValidationError


class StudentPasswordValidator:
    def __init__(self):
        self.min_length = 6
        self.help_text = (
            f"Your password must contain at least {self.min_length} characters."
        )

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(self.help_text, code="password_too_short")

    def get_help_text(self):
        return self.help_text
