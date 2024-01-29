import re

from django.core.exceptions import ValidationError


class TeacherPasswordValidator:
    def __init__(self):
        self.min_length = 10
        self.help_text = (
            f"Your password must contain at least {self.min_length} characters, 1 uppercase character, "
            f"1 lowercase character, 1 digit and 1 special character.",
        )

    def validate(self, password, user=None):
        if not (
            len(password) >= self.min_length
            and re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password)
        ):
            raise ValidationError(self.help_text, code="password_not_valid")

    def get_help_text(self):
        return self.help_text
