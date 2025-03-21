"""
© Ocado Group
Created on 21/03/2025 at 16:28:39(+00:00).
"""

from string import ascii_letters, ascii_lowercase, ascii_uppercase
from string import digits as ascii_numbers

from ...tests import ValidatorTestCase
from .ascii import (
    AsciiAlphaCharSetValidator,
    AsciiAlphanumericCharSetValidator,
    AsciiNumericCharSetValidator,
    LowercaseAsciiAlphaCharSetValidator,
    LowercaseAsciiAlphanumericCharSetValidator,
    UppercaseAsciiAlphaCharSetValidator,
    UppercaseAsciiAlphanumericCharSetValidator,
)

# pylint: disable=missing-class-docstring


class TestAsciiAlphaCharSetValidator(
    ValidatorTestCase[AsciiAlphaCharSetValidator]
):
    validator_class = AsciiAlphaCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)


class TestLowercaseAsciiAlphaCharSetValidator(
    ValidatorTestCase[LowercaseAsciiAlphaCharSetValidator]
):
    validator_class = LowercaseAsciiAlphaCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)


class TestUppercaseAsciiAlphaCharSetValidator(
    ValidatorTestCase[UppercaseAsciiAlphaCharSetValidator]
):
    validator_class = UppercaseAsciiAlphaCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)


class TestAsciiNumericCharSetValidator(
    ValidatorTestCase[AsciiNumericCharSetValidator]
):
    validator_class = AsciiNumericCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)


class TestAsciiAlphanumericCharSetValidator(
    ValidatorTestCase[AsciiAlphanumericCharSetValidator]
):
    validator_class = AsciiAlphanumericCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)


class TestLowercaseAsciiAlphanumericCharSetValidator(
    ValidatorTestCase[LowercaseAsciiAlphanumericCharSetValidator]
):
    validator_class = LowercaseAsciiAlphanumericCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)


class TestUppercaseAsciiAlphanumericCharSetValidator(
    ValidatorTestCase[UppercaseAsciiAlphanumericCharSetValidator]
):
    validator_class = UppercaseAsciiAlphanumericCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)
