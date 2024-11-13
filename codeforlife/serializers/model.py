"""
© Ocado Group
Created on 20/01/2024 at 11:19:24(+00:00).

Base model serializers.
"""

import typing as t

from django.db.models import Model
from rest_framework.serializers import ModelSerializer as _ModelSerializer

from ..request import BaseRequest, Request
from ..types import DataDict
from .base import BaseSerializer

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User
    from ..views import BaseModelViewSet, ModelViewSet

    RequestUser = t.TypeVar("RequestUser", bound=User)
    AnyBaseModelViewSet = t.TypeVar(
        "AnyBaseModelViewSet", bound=BaseModelViewSet
    )
else:
    RequestUser = t.TypeVar("RequestUser")
    AnyBaseModelViewSet = t.TypeVar("AnyBaseModelViewSet")

AnyModel = t.TypeVar("AnyModel", bound=Model)
AnyBaseRequest = t.TypeVar("AnyBaseRequest", bound=BaseRequest)
# pylint: enable=duplicate-code


class BaseModelSerializer(
    BaseSerializer[AnyBaseRequest],
    _ModelSerializer[AnyModel],
    t.Generic[AnyBaseRequest, AnyBaseModelViewSet, AnyModel],
):
    """Base model serializer for all model serializers."""

    instance: t.Optional[AnyModel]
    view: AnyBaseModelViewSet

    @property
    def non_none_instance(self):
        """Casts the instance to not None."""
        return t.cast(AnyModel, self.instance)

    # pylint: disable-next=useless-parent-delegation
    def update(self, instance: AnyModel, validated_data: DataDict) -> AnyModel:
        return super().update(instance, validated_data)

    # pylint: disable-next=useless-parent-delegation
    def create(self, validated_data: DataDict) -> AnyModel:
        return super().create(validated_data)

    def validate(self, attrs: DataDict):
        return attrs

    # pylint: disable-next=useless-parent-delegation
    def to_representation(self, instance: AnyModel) -> DataDict:
        return super().to_representation(instance)


class ModelSerializer(
    BaseModelSerializer[
        Request[RequestUser],
        "ModelViewSet[RequestUser, AnyModel]",
        AnyModel,
    ],
    t.Generic[RequestUser, AnyModel],
):
    """Base model serializer for all model serializers."""
