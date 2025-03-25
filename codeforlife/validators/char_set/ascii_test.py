"""
© Ocado Group
Created on 21/03/2025 at 16:28:39(+00:00).
"""

from string import ascii_letters, ascii_lowercase, ascii_uppercase
from string import digits as ascii_numbers

from ...tests import RegexValidatorTestCase
from ._test import (
    unicode_letters,
    unicode_lowercase,
    unicode_numbers,
    unicode_uppercase,
)
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
# pylint: disable=too-many-ancestors


class TestAsciiAlphaCharSetValidator(
    RegexValidatorTestCase[AsciiAlphaCharSetValidator]
):
    validator_class = AsciiAlphaCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_unicode_alpha(self):
        """Unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestLowercaseAsciiAlphaCharSetValidator(
    RegexValidatorTestCase[LowercaseAsciiAlphaCharSetValidator]
):
    validator_class = LowercaseAsciiAlphaCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestUppercaseAsciiAlphaCharSetValidator(
    RegexValidatorTestCase[UppercaseAsciiAlphaCharSetValidator]
):
    validator_class = UppercaseAsciiAlphaCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestAsciiNumericCharSetValidator(
    RegexValidatorTestCase[AsciiNumericCharSetValidator]
):
    validator_class = AsciiNumericCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_letters)

    def test_unicode_alpha(self):
        """Unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestAsciiAlphanumericCharSetValidator(
    RegexValidatorTestCase[AsciiAlphanumericCharSetValidator]
):
    validator_class = AsciiAlphanumericCharSetValidator

    def test_ascii_alpha(self):
        """ASCII alpha characters are in the set."""
        self.validator_class()(ascii_letters)

    def test_unicode_alpha(self):
        """Unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_letters)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestLowercaseAsciiAlphanumericCharSetValidator(
    RegexValidatorTestCase[LowercaseAsciiAlphanumericCharSetValidator]
):
    validator_class = LowercaseAsciiAlphanumericCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_lowercase)

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_uppercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestUppercaseAsciiAlphanumericCharSetValidator(
    RegexValidatorTestCase[UppercaseAsciiAlphanumericCharSetValidator]
):
    validator_class = UppercaseAsciiAlphanumericCharSetValidator

    def test_lowercase_ascii_alpha(self):
        """Lowercase ASCII alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(ascii_lowercase)

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_ascii_alpha(self):
        """Uppercase ASCII alpha characters are in the set."""
        self.validator_class()(ascii_uppercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_ascii_numbers(self):
        """ASCII numbers are in the set."""
        self.validator_class()(ascii_numbers)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)
