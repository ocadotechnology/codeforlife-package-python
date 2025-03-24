"""
© Ocado Group
Created on 14/03/2025 at 10:04:16(+00:00).
"""

import typing as t

from django.core.validators import RegexValidator

from .test import TestCase

AnyValidator = t.TypeVar("AnyValidator", bound=t.Callable)
AnyRegexValidator = t.TypeVar("AnyRegexValidator", bound=RegexValidator)


class ValidatorTestCase(TestCase, t.Generic[AnyValidator]):
    """Test case with utilities for testing validators."""

    validator_class: t.Type[AnyValidator]


class RegexValidatorTestCase(
    ValidatorTestCase[AnyRegexValidator], t.Generic[AnyRegexValidator]
):
    """Test case with utilities for testing regex validators."""

    def assert_raises_validation_error(self, *args, **kwargs):
        return super().assert_raises_validation_error(
            self.validator_class.code, *args, **kwargs
        )
