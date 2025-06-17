"""
© Ocado Group
Created on 30/01/2024 at 18:06:31(+00:00).

Base test case for all model serializers.
"""

import typing as t
from copy import deepcopy
from unittest.case import _AssertRaisesContext

from django.db.models import Model
from django.forms.models import model_to_dict
from rest_framework.serializers import BaseSerializer, ValidationError

from ..serializers import (
    BaseModelListSerializer,
    BaseModelSerializer,
    ModelSerializer,
)
from ..types import DataDict, get_arg
from .api_request_factory import APIRequestFactory, BaseAPIRequestFactory
from .test import TestCase

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
else:
    RequestUser = t.TypeVar("RequestUser")

AnyModel = t.TypeVar("AnyModel", bound=Model)
AnyBaseModelSerializer = t.TypeVar(
    "AnyBaseModelSerializer", bound=BaseModelSerializer
)
AnyBaseAPIRequestFactory = t.TypeVar(
    "AnyBaseAPIRequestFactory", bound=BaseAPIRequestFactory
)
# pylint: enable=duplicate-code


class BaseModelSerializerTestCase(
    TestCase,
    t.Generic[AnyBaseModelSerializer, AnyBaseAPIRequestFactory, AnyModel],
):
    """Base for all model serializer test cases."""

    model_serializer_class: t.Type[AnyBaseModelSerializer]

    request_factory: AnyBaseAPIRequestFactory
    request_factory_class: t.Type[AnyBaseAPIRequestFactory]

    REQUIRED_ATTRS: t.Set[str] = {
        "model_serializer_class",
        "request_factory_class",
    }

    @classmethod
    def _initialize_request_factory(cls, **kwargs):
        return cls.request_factory_class(**kwargs)

    @classmethod
    def setUpClass(cls):
        for attr in cls.REQUIRED_ATTRS:
            assert hasattr(cls, attr), f'Attribute "{attr}" must be set.'

        cls.request_factory = cls._initialize_request_factory()

        return super().setUpClass()

    # --------------------------------------------------------------------------
    # Private helpers.
    # --------------------------------------------------------------------------

    NonModelFields = t.Union[t.Set[str], t.Dict[str, "NonModelFields"]]

    def _init_model_serializer(
        self, *args, parent: t.Optional[BaseSerializer] = None, **kwargs
    ):
        serializer = self.model_serializer_class(*args, **kwargs)
        if parent:
            serializer.parent = parent

        return serializer

    def _get_data(
        self,
        validated_data: DataDict,
        new_data: t.Optional[DataDict],
        non_model_fields: t.Optional[NonModelFields],
    ):
        data = deepcopy(validated_data)

        def merge(data: DataDict, new_data: DataDict):
            for field, new_value in new_data.items():
                if isinstance(new_value, dict):
                    value = data.setdefault(field, {})
                    merge(value, new_value)
                else:
                    data[field] = new_value

        if new_data:
            merge(data, new_data)

        def pop_non_model_fields(
            data: DataDict,
            non_model_fields: ModelSerializerTestCase.NonModelFields,
        ):
            if isinstance(non_model_fields, dict):
                for field, _non_model_fields in non_model_fields.items():
                    pop_non_model_fields(data[field], _non_model_fields)
            else:
                for field in non_model_fields:
                    data.pop(field)

        if non_model_fields:
            pop_non_model_fields(data, non_model_fields)

        return data

    def _assert_data_is_subset_of_model(self, data: DataDict, model):
        assert isinstance(model, Model)

        for field, value in data.copy().items():
            # NOTE: A data value of type dict == a foreign object on the model.
            if isinstance(value, dict):
                self._assert_data_is_subset_of_model(
                    value, getattr(model, field)
                )
                data.pop(field)
            elif isinstance(value, Model):
                data[field] = getattr(value, "id")

        model_dict = model_to_dict(model)
        self.assertDictEqual(model_dict | data, model_dict)

    def _assert_new_data_is_subset_of_data(self, new_data: DataDict, data):
        assert isinstance(data, dict)

        for field, new_value in new_data.items():
            value = data[field]
            if isinstance(new_value, dict):
                self._assert_new_data_is_subset_of_data(new_value, value)
            else:
                assert new_value == value

    def _assert_many(
        self,
        validated_data: t.List[DataDict],
        new_data: t.Optional[t.List[DataDict]],
        non_model_fields: t.Optional[NonModelFields],
        get_models: t.Callable[
            [BaseModelListSerializer[t.Any, t.Any, AnyModel], t.List[DataDict]],
            t.List[AnyModel],
        ],
        *args,
        **kwargs,
    ):
        assert validated_data
        if new_data is None:
            new_data = [{} for _ in range(len(validated_data))]
        else:
            assert len(new_data) == len(validated_data)

        kwargs.pop("many", None)  # many must be True
        serializer: BaseModelListSerializer[t.Any, t.Any, AnyModel] = (
            self._init_model_serializer(*args, **kwargs, many=True)
        )

        models = get_models(serializer, deepcopy(validated_data))
        assert len(models) == len(validated_data)

        for data, _new_data, model in zip(validated_data, new_data, models):
            data = self._get_data(data, _new_data, non_model_fields)
            self._assert_data_is_subset_of_model(data, model)

    # --------------------------------------------------------------------------
    # Public helpers.
    # --------------------------------------------------------------------------

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

    def assert_validate(
        self,
        attrs: t.Union[DataDict, t.List[DataDict]],
        error_code: str,
        *args,
        **kwargs,
    ):
        """Asserts that calling validate() raises the expected error code.

        Args:
            attrs: The attributes to pass to validate().
            error_code: The expected error code to be raised.
        """
        serializer = self._init_model_serializer(*args, **kwargs)
        with self.assert_raises_validation_error(error_code):
            serializer.validate(attrs)  # type: ignore[arg-type]

    # pylint: disable-next=too-many-arguments
    def assert_validate_field(
        self, name: str, error_code: str, *args, value=None, **kwargs
    ):
        """Asserts that calling validate_field() raises the expected error code.

        Args:
            name: The name of the field.
            error_code: The expected error code to be raised.
            value: The value to pass to validate_field().
        """
        serializer = self._init_model_serializer(*args, **kwargs)
        validate_field = getattr(serializer, f"validate_{name}")
        assert callable(validate_field)
        with self.assert_raises_validation_error(error_code):
            validate_field(value)

    def assert_create(
        self,
        validated_data: DataDict,
        *args,
        new_data: t.Optional[DataDict] = None,
        non_model_fields: t.Optional[NonModelFields] = None,
        **kwargs,
    ):
        """Assert that the data used to create the model is a subset of the
        model's data.

        Args:
            validated_data: The data used to create the model.
            new_data: Any new data that the model may have after creating.
            non_model_fields: Validated data fields that are not in the model.
        """
        serializer = self._init_model_serializer(*args, **kwargs)
        model = serializer.create(deepcopy(validated_data))
        data = self._get_data(validated_data, new_data, non_model_fields)
        self._assert_data_is_subset_of_model(data, model)

    def assert_create_many(
        self,
        validated_data: t.List[DataDict],
        *args,
        new_data: t.Optional[t.List[DataDict]] = None,
        non_model_fields: t.Optional[NonModelFields] = None,
        **kwargs,
    ):
        """Assert that the data used to create the models is a subset of the
        models' data.

        Use this assert helper instead of "assert_create" if the create() on a
        list serializer is being called.

        Args:
            instance: The model instances to create.
            validated_data: The data used to create the models.
            new_data: Any new data that the models may have after creation.
            non_model_fields: Validated data fields that are not in the model.
        """
        self._assert_many(
            validated_data,
            new_data,
            non_model_fields,
            lambda serializer, validated_data: serializer.create(
                validated_data
            ),
            *args,
            **kwargs,
        )

    def assert_update(
        self,
        instance: AnyModel,
        validated_data: DataDict,
        *args,
        new_data: t.Optional[DataDict] = None,
        non_model_fields: t.Optional[NonModelFields] = None,
        **kwargs,
    ):
        """Assert that the data used to update the model is a subset of the
        model's data.

        Args:
            instance: The model instance to update.
            validated_data: The data used to update the model.
            new_data: Any new data that the model may have after updating.
            non_model_fields: Validated data fields that are not in the model.
        """
        serializer = self._init_model_serializer(*args, **kwargs)
        model = serializer.update(instance, deepcopy(validated_data))
        data = self._get_data(validated_data, new_data, non_model_fields)
        self._assert_data_is_subset_of_model(data, model)

    def assert_update_many(
        self,
        instance: t.List[AnyModel],
        validated_data: t.List[DataDict],
        *args,
        new_data: t.Optional[t.List[DataDict]] = None,
        non_model_fields: t.Optional[NonModelFields] = None,
        **kwargs,
    ):
        """Assert that the data used to update the models is a subset of the
        models' data.

        Use this assert helper instead of "assert_update" if the update() on a
        list serializer is being called.

        Args:
            instance: The model instances to update.
            validated_data: The data used to update the models.
            new_data: Any new data that the models may have after updating.
            non_model_fields: Validated data fields that are not in the model.
        """
        assert len(instance) == len(validated_data)

        self._assert_many(
            validated_data,
            new_data,
            non_model_fields,
            lambda serializer, validated_data: serializer.update(
                instance, validated_data
            ),
            *args,
            **kwargs,
        )

    def assert_to_representation(
        self,
        instance: AnyModel,
        new_data: DataDict,
        *args,
        non_model_fields: t.Optional[NonModelFields] = None,
        **kwargs,
    ):
        """Assert:
        1. the new data fields not contained in the model are equal.
        2. the original data fields contained in the model are equal.

        Args:
            instance: The model instance to represent.
            new_data: The field values not contained in the model.
            non_model_fields: Data fields that are not in the model.
        """
        serializer = self._init_model_serializer(*args, **kwargs)
        data = serializer.to_representation(instance)

        self._assert_new_data_is_subset_of_data(new_data, data)
        data = self._get_data(data, None, non_model_fields)
        self._assert_data_is_subset_of_model(data, instance)


class ModelSerializerTestCase(
    BaseModelSerializerTestCase[
        ModelSerializer[RequestUser, AnyModel],
        APIRequestFactory[RequestUser],
        AnyModel,
    ],
    t.Generic[RequestUser, AnyModel],
):
    """Base for all model serializer test cases."""

    request_factory_class = APIRequestFactory

    @classmethod
    def get_request_user_class(cls) -> t.Type[AnyModel]:
        """Get the model view set's class.

        Returns:
            The model view set's class.
        """
        return get_arg(cls, 0)

    @classmethod
    def get_model_class(cls) -> t.Type[AnyModel]:
        """Get the model view set's class.

        Returns:
            The model view set's class.
        """
        return get_arg(cls, 1)

    @classmethod
    def _initialize_request_factory(cls, **kwargs):
        kwargs["user_class"] = cls.get_request_user_class()
        return super()._initialize_request_factory(**kwargs)
