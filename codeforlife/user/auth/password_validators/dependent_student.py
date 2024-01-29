from django.core.exceptions import ValidationError


class DependentStudentPasswordValidator:
    def __init__(self):
        self.min_length = 6
        self.help_text = (
            f"Your password must contain at least {self.min_length} characters."
        )

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(self.help_text, code="password_not_valid")

    def get_help_text(self):
        return self.help_text
