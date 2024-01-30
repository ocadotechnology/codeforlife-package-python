"""
© Ocado Group
Created on 30/01/2024 at 18:06:31(+00:00).

Base test case for all model serializers.
"""

import typing as t

from django.db.models import Model
from django.test import TestCase
from rest_framework.serializers import ValidationError

from ..serializers import ModelSerializer

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelSerializerTestCase(TestCase, t.Generic[AnyModel]):
    """Base for all model serializer test cases."""

    model_serializer_class: t.Type[ModelSerializer[AnyModel]]

    @classmethod
    def get_model_class(cls) -> t.Type[AnyModel]:
        """Get the model view set's class.

        Returns:
            The model view set's class.
        """

        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

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
                assert self.context.exception.detail[0].code == code
                return value

        return ContextWrapper(context)
