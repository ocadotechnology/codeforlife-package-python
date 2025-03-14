"""
© Ocado Group
Created on 14/03/2025 at 10:04:16(+00:00).
"""

import typing as t

from .test import TestCase

AnyValidator = t.TypeVar("AnyValidator", bound=t.Callable)


class ValidatorTestCase(TestCase, t.Generic[AnyValidator]):
    """Test case with utilities for testing validators."""

    validator_class: t.Type[AnyValidator]

    def assert_raises_validation_error(self, *args, **kwargs):
        return super().assert_raises_validation_error(
            "invalid", *args, **kwargs
        )
