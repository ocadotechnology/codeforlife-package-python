"""
© Ocado Group
Created on 20/01/2024 at 11:19:24(+00:00).

Base model serializers.
"""

import typing as t

from django.db.models import Model
from rest_framework.serializers import ModelSerializer as _ModelSerializer

from ..types import DataDict
from .base import BaseSerializer

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
else:
    RequestUser = t.TypeVar("RequestUser")

AnyModel = t.TypeVar("AnyModel", bound=Model)
# pylint: enable=duplicate-code


class ModelSerializer(
    BaseSerializer[RequestUser],
    _ModelSerializer[AnyModel],
    t.Generic[RequestUser, AnyModel],
):
    """Base model serializer for all model serializers."""

    instance: t.Optional[AnyModel]

    @property
    def view(self):
        # NOTE: import outside top-level to avoid circular imports.
        # pylint: disable-next=import-outside-toplevel
        from ..views import ModelViewSet

        return t.cast(ModelViewSet[RequestUser, AnyModel], super().view)

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
