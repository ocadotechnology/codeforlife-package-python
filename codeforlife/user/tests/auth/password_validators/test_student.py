"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""

from .password_validator import PasswordValidatorTestCase
from ....auth.password_validators import StudentPasswordValidator
from ....models.user import User


class TestStudentPasswordValidator(PasswordValidatorTestCase):
    user = User.objects.filter(new_student__isnull=False).first()
    validator = StudentPasswordValidator()

    def test_validate__password_too_short(self):
        password = "fxwSn"

        with self.assert_raises_validation_error("password_too_short"):
            self.validator.validate(password, self.user)
