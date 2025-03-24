"""
© Ocado Group
Created on 21/03/2025 at 16:29:12(+00:00).
"""

from ...tests import RegexValidatorTestCase
from ._test import (
    unicode_letters,
    unicode_lowercase,
    unicode_numbers,
    unicode_uppercase,
)
from .unicode import (
    LowercaseUnicodeAlphaCharSetValidator,
    LowercaseUnicodeAlphanumericCharSetValidator,
    UnicodeAlphaCharSetValidator,
    UnicodeAlphanumericCharSetValidator,
    UnicodeNumericCharSetValidator,
    UppercaseUnicodeAlphaCharSetValidator,
    UppercaseUnicodeAlphanumericCharSetValidator,
)

# pylint: disable=missing-class-docstring
# pylint: disable=too-many-ancestors


class TestUnicodeAlphaCharSetValidator(
    RegexValidatorTestCase[UnicodeAlphaCharSetValidator]
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
    RegexValidatorTestCase[LowercaseUnicodeAlphaCharSetValidator]
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
    RegexValidatorTestCase[UppercaseUnicodeAlphaCharSetValidator]
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
    RegexValidatorTestCase[UnicodeNumericCharSetValidator]
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
    RegexValidatorTestCase[UnicodeAlphanumericCharSetValidator]
):
    validator_class = UnicodeAlphanumericCharSetValidator

    def test_unicode_alpha(self):
        """Unicode alpha characters are in the set."""
        self.validator_class()(unicode_letters)

    def test_unicode_numbers(self):
        """Unicode numbers are in the set."""
        self.validator_class()(unicode_numbers)


class TestLowercaseUnicodeAlphanumericCharSetValidator(
    RegexValidatorTestCase[LowercaseUnicodeAlphanumericCharSetValidator]
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
    RegexValidatorTestCase[UppercaseUnicodeAlphanumericCharSetValidator]
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
