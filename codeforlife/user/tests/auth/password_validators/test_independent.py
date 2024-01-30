"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""

from .password_validator import PasswordValidatorTestCase
from ....auth.password_validators import IndependentPasswordValidator
from ....models.user import User


class TestIndependentPasswordValidator(PasswordValidatorTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.filter(
            new_teacher__isnull=True, new_student__isnull=True
        ).first()
        cls.validator = IndependentPasswordValidator()
        super(TestIndependentPasswordValidator, cls).setUpClass()

    def test_validate__password_too_short(self):
        password = "fxwSn4}"

        with self.assert_raises_validation_error("password_too_short"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_uppercase(self):
        password = ">28v*@a)-{"

        with self.assert_raises_validation_error("password_no_uppercase"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_lowercase(self):
        password = "F:6]LH!_5>"

        with self.assert_raises_validation_error("password_no_lowercase"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_digit(self):
        password = "{$#FJdxGvs"

        with self.assert_raises_validation_error("password_no_digit"):
            self.validator.validate(password, self.user)
