"""
© Ocado Group
Created on 06/11/2024 at 12:45:33(+00:00).

Base test case for all model list serializers.
"""

import typing as t

from django.db.models import Model

from ..serializers import (
    BaseModelListSerializer,
    BaseModelSerializer,
    ModelListSerializer,
    ModelSerializer,
)
from ..types import DataDict
from .api_request_factory import APIRequestFactory, BaseAPIRequestFactory
from .model_serializer import (
    BaseModelSerializerTestCase,
    ModelSerializerTestCase,
)

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
AnyBaseModelListSerializer = t.TypeVar(
    "AnyBaseModelListSerializer", bound=BaseModelListSerializer
)
AnyBaseAPIRequestFactory = t.TypeVar(
    "AnyBaseAPIRequestFactory", bound=BaseAPIRequestFactory
)
# pylint: enable=duplicate-code


class BaseModelListSerializerTestCase(
    BaseModelSerializerTestCase[
        AnyBaseModelSerializer,
        AnyBaseAPIRequestFactory,
        AnyModel,
    ],
    t.Generic[
        AnyBaseModelListSerializer,
        AnyBaseModelSerializer,
        AnyBaseAPIRequestFactory,
        AnyModel,
    ],
):
    """Base for all model serializer test cases."""

    model_list_serializer_class: t.Type[AnyBaseModelListSerializer]

    REQUIRED_ATTRS = {
        "model_list_serializer_class",
        "model_serializer_class",
        "request_factory_class",
    }

    def _init_model_serializer(self, *args, parent=None, **kwargs):
        kwargs.setdefault("child", self.model_serializer_class())
        serializer = self.model_list_serializer_class(*args, **kwargs)
        if parent:
            serializer.parent = parent

        return serializer

    def assert_to_representation(
        self,
        instance: t.List[AnyModel],  # type: ignore[override]
        new_data: t.List[DataDict],  # type: ignore[override]
        *args,
        non_model_fields=None,
        **kwargs
    ):
        assert len(instance) == len(new_data)

        serializer = self._init_model_serializer(*args, **kwargs)
        data = serializer.to_representation(instance)

        for model, _new_data, _data in zip(instance, new_data, data):
            self._assert_new_data_is_subset_of_data(_new_data, _data)
            _data = self._get_data(_data, None, non_model_fields)
            self._assert_data_is_subset_of_model(_data, model)


# pylint: disable-next=too-many-ancestors
class ModelListSerializerTestCase(
    BaseModelListSerializerTestCase[
        ModelListSerializer[RequestUser, AnyModel],
        ModelSerializer[RequestUser, AnyModel],
        APIRequestFactory[RequestUser],
        AnyModel,
    ],
    ModelSerializerTestCase[RequestUser, AnyModel],
    t.Generic[RequestUser, AnyModel],
):
    """Base for all model serializer test cases."""
