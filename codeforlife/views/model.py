"""
© Ocado Group
Created on 24/01/2024 at 13:08:23(+00:00).
"""

import typing as t

from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.viewsets import ModelViewSet as DrfModelViewSet

from ..permissions import Permission
from ..serializers import ModelListSerializer, ModelSerializer
from .api import APIView

AnyModel = t.TypeVar("AnyModel", bound=Model)

if t.TYPE_CHECKING:
    # NOTE: This raises an error during runtime.
    # pylint: disable-next=too-few-public-methods
    class _ModelViewSet(DrfModelViewSet[AnyModel], t.Generic[AnyModel]):
        pass

else:
    # pylint: disable-next=too-many-ancestors
    class _ModelViewSet(DrfModelViewSet, t.Generic[AnyModel]):
        pass


# pylint: disable-next=too-many-ancestors
class ModelViewSet(APIView, _ModelViewSet[AnyModel], t.Generic[AnyModel]):
    """Base model view set for all model view sets."""

    serializer_class: t.Optional[t.Type[ModelSerializer[AnyModel]]]

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

    def get_permissions(self):
        return t.cast(t.List[Permission], super().get_permissions())

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)

        if self.action == "bulk":
            list_serializer = t.cast(ListSerializer, serializer)

            meta = getattr(list_serializer.child, "Meta", None)
            if meta is None:
                # pylint: disable-next=missing-class-docstring,too-few-public-methods
                class Meta:
                    pass

                meta = Meta
                setattr(list_serializer.child, "Meta", meta)

            if getattr(meta, "list_serializer_class", None) is None:
                model_class = self.get_model_class()

                # pylint: disable-next=too-few-public-methods
                class _ModelListSerializer(
                    ModelListSerializer[model_class]  # type: ignore[valid-type]
                ):
                    pass

                # Set list_serializer_class to default if not set.
                setattr(meta, "list_serializer_class", _ModelListSerializer)

                # Get default list_serializer_class.
                serializer = super().get_serializer(*args, **kwargs)

        return serializer

    def bulk_create(self, request: Request):
        """Bulk create many instances of a model.

        This is an extension of the default create action:
        https://www.django-rest-framework.org/api-guide/generic-views/#createmodelmixin

        Args:
            request: A HTTP request containing a list of models to create.

        Returns:
            A HTTP response containing a list of created models.
        """

        serializer = t.cast(
            ModelListSerializer[AnyModel],
            self.get_serializer(data=request.data, many=True),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )

    def perform_bulk_create(self, serializer: ModelListSerializer[AnyModel]):
        """Bulk create many instances of a model.

        Args:
            serializer: A model serializer for the specific model.
        """

        serializer.save()

    def bulk_partial_update(self, request: Request):
        # pylint: disable=line-too-long
        """Partially bulk update many instances of a model.

        This is an extension of the default partial-update action:
        https://www.django-rest-framework.org/api-guide/generic-views/#updatemodelmixin

        Args:
            request: A HTTP request containing a list of models to partially update.

        Returns:
            A HTTP response containing a list of partially updated models.
        """
        # pylint: enable=line-too-long

        model_class = self.get_model_class()
        lookup_field = (
            model_class._meta.pk.attname  # type: ignore[union-attr]
            if self.lookup_field == "pk"
            else self.lookup_field
        )

        data = t.cast(t.List[t.Dict[str, t.Any]], request.data)
        data.sort(key=lambda model: model[lookup_field])

        queryset = model_class.objects.filter(  # type: ignore[attr-defined]
            **{f"{lookup_field}__in": [model[lookup_field] for model in data]}
        ).order_by(lookup_field)

        serializer = t.cast(
            ModelListSerializer[AnyModel],
            self.get_serializer(
                list(queryset),
                data=data,
                many=True,
                partial=True,
            ),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)

    def perform_bulk_update(self, serializer: ModelListSerializer[AnyModel]):
        """Partially bulk update many instances of a model.

        Args:
            serializer: A model serializer for the specific model.
        """

        serializer.save()

    def bulk_destroy(self, request: Request):
        """Bulk destroy many instances of a model.

        This is an extension of the default destroy action:
        https://www.django-rest-framework.org/api-guide/generic-views/#destroymodelmixin

        Args:
            request: A HTTP request containing a list of models to destroy.

        Returns:
            A HTTP response containing a list of destroyed models.
        """

        model_class = self.get_model_class()
        queryset = model_class.objects.filter(  # type: ignore[attr-defined]
            **{f"{self.lookup_field}__in": request.data}
        )
        self.perform_bulk_destroy(queryset)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, queryset: QuerySet[AnyModel]):
        """Bulk destroy many instances of a model.

        Args:
            queryset: A queryset of the models to delete.
        """

        queryset.delete()

    @action(detail=False, methods=["post", "patch", "delete"])
    def bulk(self, request: Request):
        """Entry point for all bulk actions.

        Args:
            request: A HTTP request.

        Returns:
            A HTTP response.
        """

        return {
            "POST": self.bulk_create,
            "PATCH": self.bulk_partial_update,
            "DELETE": self.bulk_destroy,
        }[t.cast(str, request.method)](request)
