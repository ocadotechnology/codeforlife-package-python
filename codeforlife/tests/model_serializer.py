"""
© Ocado Group
Created on 30/01/2024 at 18:06:31(+00:00).

Base test case for all model serializers.
"""

import typing as t
from unittest.case import _AssertRaisesContext

from django.db.models import Model
from django.forms.models import model_to_dict
from django.test import TestCase
from rest_framework.serializers import BaseSerializer, ValidationError

from ..serializers import ModelSerializer
from ..types import DataDict
from .api_request_factory import APIRequestFactory

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

        class Wrapper:
            """Wrap context to assert code on exit."""

            def __init__(self, ctx: "_AssertRaisesContext[ValidationError]"):
                self.ctx = ctx

            def __enter__(self, *args, **kwargs):
                return self.ctx.__enter__(*args, **kwargs)

            def __exit__(self, *args, **kwargs):
                value = self.ctx.__exit__(*args, **kwargs)
                assert (
                    code
                    == self.ctx.exception.detail[  # type: ignore[union-attr]
                        0  # type: ignore[index]
                    ].code
                )
                return value

        return Wrapper(self.assertRaises(ValidationError, *args, **kwargs))

    def _init_model_serializer(
        self,
        parent: t.Optional[BaseSerializer],
        *args,
        **kwargs,
    ):
        serializer = self.model_serializer_class(*args, **kwargs)
        if parent:
            serializer.parent = parent

        return serializer

    def assert_validate(
        self,
        attrs: t.Union[DataDict, t.List[DataDict]],
        error_code: str,
        *args,
        parent: t.Optional[BaseSerializer] = None,
        **kwargs,
    ):
        """Asserts that calling validate() raises the expected error code.

        Args:
            attrs: The attributes to pass to validate().
            error_code: The expected error code to be raised.
            parent: The parent serializer that instantiated this serializer.
        """

        serializer = self._init_model_serializer(parent, *args, **kwargs)
        with self.assert_raises_validation_error(error_code):
            serializer.validate(attrs)  # type: ignore[arg-type]

    # pylint: disable-next=too-many-arguments
    def assert_validate_field(
        self,
        name: str,
        value,
        error_code: str,
        *args,
        parent: t.Optional[BaseSerializer] = None,
        **kwargs,
    ):
        """Asserts that calling validate_field() raises the expected error code.

        Args:
            name: The name of the field.
            value: The value to pass to validate_field().
            error_code: The expected error code to be raised.
            parent: The parent serializer that instantiated this serializer.
        """

        serializer = self._init_model_serializer(parent, *args, **kwargs)
        validate_field = getattr(serializer, f"validate_{name}")
        assert callable(validate_field)
        with self.assert_raises_validation_error(error_code):
            validate_field(value)

    def _assert_data_is_subset_of_model(self, data: DataDict, model):
        assert isinstance(model, Model)

        for field, value in data.copy().items():
            # NOTE: A data value of type dict == a foreign object on the model.
            if isinstance(value, dict):
                self._assert_data_is_subset_of_model(
                    value,
                    getattr(model, field),
                )
                data.pop(field)

        self.assertDictContainsSubset(data, model_to_dict(model))

    def assert_create(
        self,
        validated_data: DataDict,
        *args,
        new_data: t.Optional[DataDict] = None,
        parent: t.Optional[BaseSerializer] = None,
        **kwargs,
    ):
        """Assert that the data used to create the model is a subset of the
        model's data.

        Args:
            validated_data: The data used to create the model.
            new_data: Any new data that the model may have after creating.
            parent: The parent serializer that instantiated this serializer.
        """

        serializer = self._init_model_serializer(parent, *args, **kwargs)
        model = serializer.create(validated_data.copy())
        data = {**validated_data, **(new_data or {})}
        self._assert_data_is_subset_of_model(data, model)

    def assert_update(
        self,
        instance: AnyModel,
        validated_data: DataDict,
        *args,
        new_data: t.Optional[DataDict] = None,
        parent: t.Optional[BaseSerializer] = None,
        **kwargs,
    ):
        """Assert that the data used to update the model is a subset of the
        model's data.

        Args:
            instance: The model instance to update.
            validated_data: The data used to update the model.
            new_data: Any new data that the model may have after updating.
            parent: The parent serializer that instantiated this serializer.
        """

        serializer = self._init_model_serializer(parent, *args, **kwargs)
        model = serializer.update(instance, validated_data.copy())
        data = {**validated_data, **(new_data or {})}
        self._assert_data_is_subset_of_model(data, model)
