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

from ..types import DataDict, OrderedDataDict
from .base import BaseSerializer

AnyModel = t.TypeVar("AnyModel", bound=Model)


BulkCreateDataList = t.List[DataDict]
BulkUpdateDataDict = t.Dict[t.Any, DataDict]
Data = t.Union[BulkCreateDataList, BulkUpdateDataDict]


class ModelSerializer(
    BaseSerializer,
    _ModelSerializer[AnyModel],
    t.Generic[AnyModel],
):
    """Base model serializer for all model serializers."""

    instance: t.Optional[AnyModel]

    @property
    def view(self):
        # NOTE: import outside top-level to avoid circular imports.
        # pylint: disable-next=import-outside-toplevel
        from ..views import ModelViewSet

        return t.cast(ModelViewSet[AnyModel], super().view)

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

    instance: t.Optional[t.List[AnyModel]]
    batch_size: t.Optional[int] = None

    @property
    def view(self):
        # NOTE: import outside top-level to avoid circular imports.
        # pylint: disable-next=import-outside-toplevel
        from ..views import ModelViewSet

        return t.cast(ModelViewSet[AnyModel], super().view)

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

    def __init__(self, *args, **kwargs):
        instance = args[0] if args else kwargs.pop("instance")
        if not isinstance(instance, list):
            instance = list(instance)

        super().__init__(instance, *args[1:], **kwargs)

    def create(self, validated_data: t.List[DataDict]) -> t.List[AnyModel]:
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
        validated_data: t.List[DataDict],
    ) -> t.List[AnyModel]:
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

    def validate(self, attrs: t.List[DataDict]):
        # If performing a bulk create.
        if self.instance is None:
            if len(attrs) == 0:
                raise _ValidationError(
                    "Nothing to create.",
                    code="nothing_to_create",
                )

        # Else, performing a bulk update.
        else:
            if len(attrs) == 0:
                raise _ValidationError(
                    "Nothing to update.",
                    code="nothing_to_update",
                )
            if len(attrs) != len(self.instance):
                raise _ValidationError(
                    "Some models do not exist.",
                    code="models_do_not_exist",
                )

        return attrs

    def to_internal_value(self, data: Data):
        # If performing a bulk create.
        if self.instance is None:
            data = t.cast(BulkCreateDataList, data)

            return t.cast(
                t.List[OrderedDataDict],
                super().to_internal_value(data),
            )

        # Else, performing a bulk update.
        data = t.cast(BulkUpdateDataDict, data)
        data_items = list(data.items())

        # Models and data are required to be sorted by the lookup field.
        data_items.sort(key=lambda item: item[0])
        self.instance.sort(
            key=lambda model: getattr(model, self.view.lookup_field)
        )

        return t.cast(
            t.List[OrderedDataDict],
            super().to_internal_value([item[1] for item in data_items]),
        )

    # pylint: disable-next=useless-parent-delegation,arguments-renamed
    def to_representation(self, instance: t.List[AnyModel]) -> t.List[DataDict]:
        return super().to_representation(instance)
