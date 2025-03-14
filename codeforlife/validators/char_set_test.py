"""
© Ocado Group
Created on 14/03/2025 at 09:18:06(+00:00).
"""

from string import (
    ascii_letters,
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation,
)

from ..tests import ValidatorTestCase
from .char_set import (
    AlphaCharSetValidator,
    AlphanumericCharSetValidator,
    CharSetValidator,
    CharSetValidatorBuilder,
    LowercaseAlphaCharSetValidator,
    LowercaseAlphanumericCharSetValidator,
    NumericCharSetValidator,
    UppercaseAlphaCharSetValidator,
    UppercaseAlphanumericCharSetValidator,
)

# pylint: disable=missing-class-docstring


class TestCharSetValidator(ValidatorTestCase[CharSetValidator]):
    validator_class = CharSetValidator

    def test_alphanumeric(self):
        """Alphanumeric characters are in the set."""
        validator = self.validator_class("a-zA-Z0-9", "alphanumeric characters")
        validator("")  # empty strings must be valid
        validator(ascii_letters + digits)
        with self.assert_raises_validation_error():
            validator(punctuation)


class TestCharSetValidatorBuilder(ValidatorTestCase[CharSetValidatorBuilder]):
    validator_class = CharSetValidatorBuilder

    def test_alphanumeric(self):
        """
        Alphanumeric characters + spaces + special characters are in the set.
        """
        validator = self.validator_class(
            "a-zA-Z0-9",
            "alphanumeric characters",
            spaces=True,
            special_chars="!-?",
        )
        validator("abc ABC 123 !?-")
        with self.assert_raises_validation_error():
            validator("$")


class TestAlphaCharSetValidator(ValidatorTestCase[AlphaCharSetValidator]):
    validator_class = AlphaCharSetValidator

    def test_alpha(self):
        """Alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_numbers(self):
        """Numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(digits)


class TestNumericCharSetValidator(ValidatorTestCase[NumericCharSetValidator]):
    validator_class = NumericCharSetValidator

    def test_alpha(self):
        """Alpha characters are in not the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_letters)

    def test_numbers(self):
        """Numbers are in the set."""
        self.validator_class()(digits)


class TestAlphanumericCharSetValidator(
    ValidatorTestCase[AlphanumericCharSetValidator]
):
    validator_class = AlphanumericCharSetValidator

    def test_alpha(self):
        """Alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_numbers(self):
        """Numbers are in the set."""
        self.validator_class()(digits)


class TestLowercaseAlphaCharSetValidator(
    ValidatorTestCase[LowercaseAlphaCharSetValidator]
):
    validator_class = LowercaseAlphaCharSetValidator

    def test_lowercase_alpha(self):
        """Lowercase alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_uppercase_alpha(self):
        """Uppercase alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_numbers(self):
        """Numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(digits)


class TestLowercaseAlphanumericCharSetValidator(
    ValidatorTestCase[LowercaseAlphanumericCharSetValidator]
):
    validator_class = LowercaseAlphanumericCharSetValidator

    def test_lowercase_alpha(self):
        """Lowercase alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_uppercase_alpha(self):
        """Uppercase alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_numbers(self):
        """Numbers are in the set."""
        self.validator_class()(digits)


class TestUppercaseAlphaCharSetValidator(
    ValidatorTestCase[UppercaseAlphaCharSetValidator]
):
    validator_class = UppercaseAlphaCharSetValidator

    def test_lowercase_alpha(self):
        """Lowercase alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_uppercase_alpha(self):
        """Uppercase alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_numbers(self):
        """Numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(digits)


class TestUppercaseAlphanumericCharSetValidator(
    ValidatorTestCase[UppercaseAlphanumericCharSetValidator]
):
    validator_class = UppercaseAlphanumericCharSetValidator

    def test_lowercase_alpha(self):
        """Lowercase alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_uppercase_alpha(self):
        """Uppercase alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_numbers(self):
        """Numbers are in the set."""
        self.validator_class()(digits)
