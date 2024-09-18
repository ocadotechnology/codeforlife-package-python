"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""

from ....tests import TestCase
from ...models import User
from .teacher import TeacherPasswordValidator


# pylint: disable-next=missing-class-docstring
class TestTeacherPasswordValidator(TestCase):
    def setUp(self):
        self.user = User.objects.filter(new_teacher__isnull=False).first()
        assert self.user is not None

        self.validator = TeacherPasswordValidator()

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
