"""
© Ocado Group
Created on 30/01/2024 at 18:06:31(+00:00).

Base test case for all model serializers.
"""

import typing as t

from django.db.models import Model
from django.test import TestCase
from rest_framework.serializers import ValidationError
from rest_framework.test import APIRequestFactory

from ..serializers import ModelSerializer
from ..types import KwArgs
from ..user.models import User

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelSerializerTestCase(TestCase, t.Generic[AnyModel]):
    """Base for all model serializer test cases."""

    model_serializer_class: t.Type[ModelSerializer[AnyModel]]

    request_factory = APIRequestFactory()

    @classmethod
    def setUpClass(cls):
        attr_name = "model_serializer_class"
        assert hasattr(cls, attr_name), f'Attribute "{attr_name}" must be set.'

        return super().setUpClass()

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

    # pylint: disable-next=too-many-arguments
    def _assert_validate(
        self,
        value,
        error_code: str,
        user: t.Optional[User],
        request_kwargs: t.Optional[KwArgs],
        get_validate: t.Callable[
            [ModelSerializer[AnyModel]], t.Callable[[t.Any], t.Any]
        ],
        **kwargs,
    ):
        kwargs.setdefault("context", {})
        context: t.Dict[str, t.Any] = kwargs["context"]

        if "request" not in context:
            request_kwargs = request_kwargs or {}
            request_kwargs.setdefault("method", "POST")
            request_kwargs.setdefault("path", "/")
            request_kwargs.setdefault("data", "")
            request_kwargs.setdefault("content_type", "application/json")

            request = self.request_factory.generic(**request_kwargs)
            if user is not None:
                request.user = user

            context["request"] = request

        serializer = self.model_serializer_class(**kwargs)

        with self.assert_raises_validation_error(error_code):
            get_validate(serializer)(value)

    def assert_validate(
        self,
        attrs: t.Dict[str, t.Any],
        error_code: str,
        user: t.Optional[User] = None,
        request_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        """Asserts that calling validate() raises the expected error code.

        Args:
            attrs: The attributes to pass to validate().
            error_code: The expected error code to be raised.
            user: The requesting user.
            request_kwargs: The kwargs used to initialize the request.
        """

        self._assert_validate(
            attrs,
            error_code,
            user,
            request_kwargs,
            get_validate=lambda serializer: serializer.validate,
            **kwargs,
        )

    # pylint: disable-next=too-many-arguments
    def assert_validate_field(
        self,
        name: str,
        value,
        error_code: str,
        user: t.Optional[User] = None,
        request_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        """Asserts that calling validate_field() raises the expected error code.

        Args:
            name: The name of the field.
            value: The value to pass to validate_field().
            error_code: The expected error code to be raised.
            user: The requesting user.
            request_kwargs: The kwargs used to initialize the request.
        """

        def get_validate(serializer: ModelSerializer[AnyModel]):
            validate_field = getattr(serializer, f"validate_{name}")
            assert callable(validate_field)
            return validate_field

        self._assert_validate(
            value,
            error_code,
            user,
            request_kwargs,
            get_validate,
            **kwargs,
        )
