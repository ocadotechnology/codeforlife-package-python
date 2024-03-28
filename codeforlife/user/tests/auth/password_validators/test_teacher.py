"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""
from .base import PasswordValidatorTestCase
from ....auth.password_validators import TeacherPasswordValidator
from ....models.user import User


class TestTeacherPasswordValidator(PasswordValidatorTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.filter(new_teacher__isnull=False).first()
        assert cls.user is not None

        cls.validator = TeacherPasswordValidator()
        super(TestTeacherPasswordValidator, cls).setUpClass()

    def test_validate__password_too_short(self):
        """Password cannot be too short"""
        password = "fxwSn4}PW"

        with self.assert_raises_validation_error("password_too_short"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_uppercase(self):
        """Password must contain an uppercase char"""
        password = ">28v*@a)-{"

        with self.assert_raises_validation_error("password_no_uppercase"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_lowercase(self):
        """Password must contain a lowercase char"""
        password = "F:6]LH!_5>"

        with self.assert_raises_validation_error("password_no_lowercase"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_digit(self):
        """Password must contain a digit"""
        password = "{$#FJdxGvs"

        with self.assert_raises_validation_error("password_no_digit"):
            self.validator.validate(password, self.user)

    def test_validate__password_no_special_character(self):
        """Password must contain a special char"""
        password = "kR48SsAwrE"

        with self.assert_raises_validation_error(
            "password_no_special_character"
        ):
            self.validator.validate(password, self.user)
