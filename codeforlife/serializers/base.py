"""
© Ocado Group
Created on 20/01/2024 at 11:19:24(+00:00).

Base model serializers.
"""

import typing as t

from django.db.models import Model
from rest_framework.serializers import ModelSerializer as _ModelSerializer

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelSerializer(_ModelSerializer[AnyModel], t.Generic[AnyModel]):
    """Base model serializer for all model serializers."""

    # pylint: disable-next=useless-parent-delegation
    def update(self, instance, validated_data: t.Dict[str, t.Any]):
        return super().update(instance, validated_data)

    # pylint: disable-next=useless-parent-delegation
    def create(self, validated_data: t.Dict[str, t.Any]):
        return super().create(validated_data)
