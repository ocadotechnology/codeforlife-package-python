"""
© Ocado Group
Created on 05/11/2024 at 17:53:40(+00:00).

Base model list serializers.
"""

import typing as t

from django.db.models import Model
from rest_framework.serializers import ListSerializer as _ListSerializer
from rest_framework.serializers import ValidationError as _ValidationError

from ..request import BaseRequest, Request
from ..types import DataDict, OrderedDataDict
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

BulkCreateDataList = t.List[DataDict]
BulkUpdateDataDict = t.Dict[t.Any, DataDict]
Data = t.Union[BulkCreateDataList, BulkUpdateDataDict]


class BaseModelListSerializer(
    BaseSerializer[AnyBaseRequest],
    _ListSerializer[t.List[AnyModel]],
    t.Generic[AnyBaseRequest, AnyBaseModelViewSet, AnyModel],
):
    """Base model list serializer for all model list serializers.

    Inherit this class if you wish to custom handle bulk create and/or update.

    class UserListSerializer(ModelListSerializer[User, User]):
        def create(self, validated_data):
            ...

        def update(self, instance, validated_data):
            ...

    class UserSerializer(ModelSerializer[User, User]):
        class Meta:
            model = User
            list_serializer_class = UserListSerializer
    """

    instance: t.Optional[t.List[AnyModel]]
    batch_size: t.Optional[int] = None
    view: AnyBaseModelViewSet

    @property
    def non_none_instance(self):
        """Casts the instance to not None."""
        return t.cast(t.List[AnyModel], self.instance)

    @property
    def model_class(self) -> t.Type[AnyModel]:
        """Shorthand to model class."""
        return self.view.model_class

    def __init__(self, *args, **kwargs):
        instance = args[0] if args else kwargs.pop("instance", None)
        if instance is not None and not isinstance(instance, list):
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
        # pylint: disable-next=line-too-long
        return self.model_class.objects.bulk_create(  # type: ignore[attr-defined]
            objs=[self.model_class(**data) for data in validated_data],
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

        self.model_class.objects.bulk_update(  # type: ignore[attr-defined]
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


class ModelListSerializer(
    BaseModelListSerializer[
        Request[RequestUser],
        "ModelViewSet[RequestUser, AnyModel]",
        AnyModel,
    ],
    t.Generic[RequestUser, AnyModel],
):
    """Base model list serializer for all model list serializers.

    Inherit this class if you wish to custom handle bulk create and/or update.

    class UserListSerializer(ModelListSerializer[User, User]):
        def create(self, validated_data):
            ...

        def update(self, instance, validated_data):
            ...

    class UserSerializer(ModelSerializer[User, User]):
        class Meta:
            model = User
            list_serializer_class = UserListSerializer
    """
