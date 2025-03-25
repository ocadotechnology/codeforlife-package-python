"""
© Ocado Group
Created on 21/03/2025 at 16:29:17(+00:00).
"""

from string import ascii_letters, digits, punctuation

from ...tests import RegexValidatorTestCase
from .base import CharSetValidator, CharSetValidatorBuilder

# pylint: disable=missing-class-docstring
# pylint: disable=too-many-ancestors


class TestCharSetValidator(RegexValidatorTestCase[CharSetValidator]):
    validator_class = CharSetValidator

    def setUp(self):
        self.validator = self.validator_class(
            "a-zA-Z0-9",
            "ASCII alphanumeric characters",
        )

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator(ascii_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator(digits)

    def test_special_chars(self):
        """Special characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator(punctuation)


class TestCharSetValidatorBuilder(
    RegexValidatorTestCase[CharSetValidatorBuilder]
):
    validator_class = CharSetValidatorBuilder

    def setUp(self):
        self.validator = self.validator_class(
            "a-zA-Z0-9",
            "ASCII alphanumeric characters",
            spaces=True,
            special_chars=punctuation,
        )

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator(ascii_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator(digits)

    def test_spaces(self):
        """Spaces are in the set."""
        self.validator(" ")

    def test_special_chars(self):
        """Special characters are in the set."""
        self.validator(punctuation)
