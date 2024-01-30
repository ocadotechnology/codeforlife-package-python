"""
© Ocado Group
Created on 20/01/2024 at 11:19:24(+00:00).

Base model serializers.
"""

import typing as t

from django.db.models import Model
from rest_framework.serializers import ListSerializer as _ListSerializer
from rest_framework.serializers import ModelSerializer as _ModelSerializer
from rest_framework.serializers import ValidationError as _ValidationError

from .base import BaseSerializer

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelSerializer(
    BaseSerializer,
    _ModelSerializer[AnyModel],
    t.Generic[AnyModel],
):
    """Base model serializer for all model serializers."""

    # pylint: disable-next=useless-parent-delegation
    def update(self, instance, validated_data: t.Dict[str, t.Any]):
        return super().update(instance, validated_data)

    # pylint: disable-next=useless-parent-delegation
    def create(self, validated_data: t.Dict[str, t.Any]):
        return super().create(validated_data)

    def validate(self, attrs: t.Dict[str, t.Any]):
        return attrs


class ModelListSerializer(
    BaseSerializer,
    t.Generic[AnyModel],
    _ListSerializer[t.List[AnyModel]],
):
    """Base model list serializer for all model list serializers.

    Inherit this class if you wish to custom handle bulk create and/or update.

    class UserListSerializer(ModelListSerializer[User]):
        def create(self, validated_data):
            ...

        def update(self, instance, validated_data):
            ...

    class UserSerializer(ModelSerializer[User]):
        class Meta:
            model = User
            list_serializer_class = UserListSerializer
    """

    instance: t.List[AnyModel]
    batch_size: t.Optional[int] = None

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

    def create(self, validated_data: t.List[t.Dict[str, t.Any]]):
        """Bulk create many instances of a model.

        https://www.django-rest-framework.org/api-guide/serializers/#customizing-multiple-create

        Args:
            validated_data: The data used to create the models.

        Returns:
            The models.
        """

        model_class = self.get_model_class()
        return model_class.objects.bulk_create(  # type: ignore[attr-defined]
            objs=[model_class(**data) for data in validated_data],
            batch_size=self.batch_size,
        )

    def update(
        self,
        instance: t.List[AnyModel],
        validated_data: t.List[t.Dict[str, t.Any]],
    ):
        """Bulk update many instances of a model.

        https://www.django-rest-framework.org/api-guide/serializers/#customizing-multiple-update

        Args:
            instance: The models to update.
            validated_data: The field-value pairs to update for each model.

        Returns:
            The models.
        """

        # Models and data must have equal length and be ordered the same!
        for model, data in zip(instance, validated_data):
            for field, value in data.items():
                setattr(model, field, value)

        model_class = self.get_model_class()
        model_class.objects.bulk_update(  # type: ignore[attr-defined]
            objs=instance,
            fields={field for data in validated_data for field in data.keys()},
            batch_size=self.batch_size,
        )

        return instance

    def validate(self, attrs: t.List[t.Dict[str, t.Any]]):
        # If performing a bulk create.
        if self.instance is None:
            if len(attrs) == 0:
                raise _ValidationError("Nothing to create.")

        # Else, performing a bulk update.
        else:
            if len(attrs) == 0:
                raise _ValidationError("Nothing to update.")
            if len(attrs) != len(self.instance):
                raise _ValidationError("Some models do not exist.")

        return attrs

    # pylint: disable-next=useless-parent-delegation,arguments-renamed
    def to_representation(self, instance: t.List[AnyModel]):
        return super().to_representation(instance)
