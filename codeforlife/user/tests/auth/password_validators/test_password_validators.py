import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from ....auth.password_validators import (
    TeacherPasswordValidator,
    IndependentStudentPasswordValidator,
    DependentStudentPasswordValidator,
)


class TestPasswordValidators(TestCase):
    password_no_special_char = "kR48SsAwrE"
    password_no_uppercase = ">28v*@a)-{"
    password_no_lowercase = "F:6]LH!_5>"
    password_no_digit = "{$#FJdxGvs"
    password_valid = "6]U~=X?qxY"

    bad_passwords = [
        password_no_special_char,
        password_no_uppercase,
        password_no_lowercase,
        password_no_digit,
    ]

    def test_teacher_password_validator(self):
        password_too_short = "fxwSn4}PW"

        validator = TeacherPasswordValidator()

        with pytest.raises(ValidationError):
            [
                validator.validate(bad_password)
                for bad_password in self.bad_passwords
            ]
            validator.validate(password_too_short)

        validator.validate(self.password_valid)

    def test_independent_student_password_validator(self):
        self.bad_passwords.remove(self.password_no_special_char)

        password_too_short = "fxwSn4}"

        validator = IndependentStudentPasswordValidator()

        with pytest.raises(ValidationError):
            [
                validator.validate(bad_password)
                for bad_password in self.bad_passwords
            ]
            validator.validate(password_too_short)

        validator.validate(self.password_valid)

    def test_dependent_student_password_validator(self):
        password_too_short = "fxwSn"

        validator = DependentStudentPasswordValidator()

        with pytest.raises(ValidationError):
            validator.validate(password_too_short)

        validator.validate(self.password_valid)
