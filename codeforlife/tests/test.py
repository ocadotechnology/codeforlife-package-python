"""
© Ocado Group
Created on 10/04/2024 at 13:03:00(+01:00).
"""

import typing as t
from unittest.case import _AssertRaisesContext

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import Client as _Client
from django.test import TestCase as _TestCase


class Client(_Client):
    """A Django client with type hints."""

    def generic(self, *args, **kwargs):
        return t.cast(HttpResponse, super().generic(*args, **kwargs))

    def get(self, *args, **kwargs):
        return t.cast(HttpResponse, super().get(*args, **kwargs))

    def post(self, *args, **kwargs):
        return t.cast(HttpResponse, super().post(*args, **kwargs))

    def put(self, *args, **kwargs):
        return t.cast(HttpResponse, super().put(*args, **kwargs))

    def patch(self, *args, **kwargs):
        return t.cast(HttpResponse, super().patch(*args, **kwargs))

    def delete(self, *args, **kwargs):
        return t.cast(HttpResponse, super().delete(*args, **kwargs))

    def options(self, *args, **kwargs):
        return t.cast(HttpResponse, super().options(*args, **kwargs))


class TestCase(_TestCase):
    """Base test case for all tests to inherit."""

    def assert_raises_validation_error(self, code: str, *args, **kwargs):
        """Assert code block raises a validation error.

        Args:
            code: The validation code to assert.

        Returns:
            The assert-raises context which will auto-assert the code.
        """

        class Wrapper:
            """Wrap context to assert code on exit."""

            def __init__(self, ctx: "_AssertRaisesContext[ValidationError]"):
                self.ctx = ctx

            def __enter__(self, *args, **kwargs):
                return self.ctx.__enter__(*args, **kwargs)

            def __exit__(self, *args, **kwargs):
                value = self.ctx.__exit__(*args, **kwargs)
                assert self.ctx.exception.code == code
                return value

        return Wrapper(self.assertRaises(ValidationError, *args, **kwargs))
