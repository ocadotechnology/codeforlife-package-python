"""
© Ocado Group
Created on 30/01/2024 at 19:01:00(+00:00).

Base test case for all password validators.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase


class PasswordValidatorTestCase(TestCase):
    """Base for all password validator test cases."""

    def assert_raises_validation_error(self, code: str, *args, **kwargs):
        """Assert code block raises a validation error.

        Args:
            code: The validation code to assert.

        Returns:
            The assert-raises context which will auto-assert the code.
        """

        context = self.assertRaises(ValidationError, *args, **kwargs)

        class ContextWrapper:
            """Wrap context to assert code on exit."""

            def __init__(self, context):
                self.context = context

            def __enter__(self, *args, **kwargs):
                return self.context.__enter__(*args, **kwargs)

            def __exit__(self, *args, **kwargs):
                value = self.context.__exit__(*args, **kwargs)
                print(self.context)
                assert self.context.exception.code == code
                return value

        return ContextWrapper(context)
