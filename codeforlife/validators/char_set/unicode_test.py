"""
© Ocado Group
Created on 21/03/2025 at 16:29:12(+00:00).
"""

from string import ascii_lowercase, ascii_uppercase, digits

from ...tests import ValidatorTestCase
from .unicode import (
    LowercaseUnicodeAlphaCharSetValidator,
    LowercaseUnicodeAlphanumericCharSetValidator,
    UnicodeAlphaCharSetValidator,
    UnicodeAlphanumericCharSetValidator,
    UnicodeNumericCharSetValidator,
    UppercaseUnicodeAlphaCharSetValidator,
    UppercaseUnicodeAlphanumericCharSetValidator,
)

# pylint: disable=invalid-name
unicode_lowercase = ascii_lowercase + "αβγδεζηθικλμνξοπρστυφχψω"  # greek
unicode_uppercase = ascii_uppercase + "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"  # greek
unicode_letters = unicode_lowercase + unicode_uppercase
unicode_numbers = digits + "٠١٢٣٤٥٦٧٨٩"  # arabic
# pylint: enable=invalid-name


# pylint: disable=missing-class-docstring


class TestUnicodeAlphaCharSetValidator(
    ValidatorTestCase[UnicodeAlphaCharSetValidator]
):
    validator_class = UnicodeAlphaCharSetValidator

    def test_unicode_alpha(self):
        """Unicode alpha characters are in the set."""
        self.validator_class()(unicode_letters)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestLowercaseUnicodeAlphaCharSetValidator(
    ValidatorTestCase[LowercaseUnicodeAlphaCharSetValidator]
):
    validator_class = LowercaseUnicodeAlphaCharSetValidator

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are in the set."""
        self.validator_class()(unicode_lowercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestUppercaseUnicodeAlphaCharSetValidator(
    ValidatorTestCase[UppercaseUnicodeAlphaCharSetValidator]
):
    validator_class = UppercaseUnicodeAlphaCharSetValidator

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are in the set."""
        self.validator_class()(unicode_uppercase)

    def test_unicode_numbers(self):
        """Unicode numbers are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_numbers)


class TestUnicodeNumericCharSetValidator(
    ValidatorTestCase[UnicodeNumericCharSetValidator]
):
    validator_class = UnicodeNumericCharSetValidator

    def test_unicode_alpha(self):
        """Unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_letters)

    def test_unicode_numbers(self):
        """Unicode numbers are in the set."""
        self.validator_class()(unicode_numbers)


class TestUnicodeAlphanumericCharSetValidator(
    ValidatorTestCase[UnicodeAlphanumericCharSetValidator]
):
    validator_class = UnicodeAlphanumericCharSetValidator

    def test_unicode_alpha(self):
        """Unicode alpha characters are in the set."""
        self.validator_class()(unicode_letters)

    def test_unicode_numbers(self):
        """Unicode numbers are in the set."""
        self.validator_class()(unicode_numbers)


class TestLowercaseUnicodeAlphanumericCharSetValidator(
    ValidatorTestCase[LowercaseUnicodeAlphanumericCharSetValidator]
):
    validator_class = LowercaseUnicodeAlphanumericCharSetValidator

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are in the set."""
        self.validator_class()(unicode_lowercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_uppercase)

    def test_unicode_numbers(self):
        """Unicode numbers are in the set."""
        self.validator_class()(unicode_numbers)


class TestUppercaseUnicodeAlphanumericCharSetValidator(
    ValidatorTestCase[UppercaseUnicodeAlphanumericCharSetValidator]
):
    validator_class = UppercaseUnicodeAlphanumericCharSetValidator

    def test_lowercase_unicode_alpha(self):
        """Lowercase unicode alpha characters are not in the set."""
        with self.assert_raises_validation_error():
            self.validator_class()(unicode_lowercase)

    def test_uppercase_unicode_alpha(self):
        """Uppercase unicode alpha characters are in the set."""
        self.validator_class()(unicode_uppercase)

    def test_unicode_numbers(self):
        """Unicode numbers are in the set."""
        self.validator_class()(unicode_numbers)
