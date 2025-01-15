"""
© Ocado Group
Created on 24/01/2024 at 13:08:23(+00:00).
"""

import typing as t
from functools import cached_property

from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.viewsets import ModelViewSet as DrfModelViewSet

from ..permissions import Permission
from ..request import BaseRequest, Request
from ..types import KwArgs
from .api import APIView, BaseAPIView
from .decorators import action

AnyModel = t.TypeVar("AnyModel", bound=Model)

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:  # pragma: no cover
    from ..serializers import (
        BaseModelSerializer,
        ModelListSerializer,
        ModelSerializer,
    )
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
    AnyBaseModelSerializer = t.TypeVar(
        "AnyBaseModelSerializer", bound=BaseModelSerializer
    )

    # NOTE: This raises an error during runtime.
    # pylint: disable-next=too-few-public-methods,too-many-ancestors
    class _ModelViewSet(DrfModelViewSet[AnyModel], t.Generic[AnyModel]):
        pass

else:
    RequestUser = t.TypeVar("RequestUser")
    AnyBaseModelSerializer = t.TypeVar("AnyBaseModelSerializer")

    # pylint: disable-next=too-many-ancestors
    class _ModelViewSet(DrfModelViewSet, t.Generic[AnyModel]):
        pass


AnyBaseRequest = t.TypeVar("AnyBaseRequest", bound=BaseRequest)

# pylint: enable=duplicate-code


# pylint: disable-next=too-many-ancestors
class BaseModelViewSet(
    BaseAPIView[AnyBaseRequest],
    _ModelViewSet[AnyModel],
    t.Generic[AnyBaseRequest, AnyBaseModelSerializer, AnyModel],
):
    """Base model view set for all model view sets."""

    model_class: t.Type[AnyModel]
    serializer_class: t.Optional[t.Type[AnyBaseModelSerializer]]

    REQUIRED_ATTRS: t.Set[str] = {"request_class", "model_class"}

    @cached_property
    def lookup_field_name(self):
        """The name of the lookup field."""
        return (
            self.model_class._meta.pk.attname  # type: ignore[union-attr]
            if self.lookup_field == "pk"
            else self.lookup_field
        )

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
                # pylint: disable-next=import-outside-toplevel
                from ..serializers import ModelListSerializer

                # TODO: delete this
                # # pylint: disable-next=too-few-public-methods
                # class _ModelListSerializer(
                #     ModelListSerializer[
                #         RequestUser,
                #         self.model_class,  # type: ignore[valid-type]
                #     ]
                # ):
                #     pass
                # Set list_serializer_class to default if not set.
                setattr(meta, "list_serializer_class", ModelListSerializer)

                # Get default list_serializer_class.
                serializer = super().get_serializer(*args, **kwargs)

        return serializer

    # pylint: disable=useless-parent-delegation

    def destroy(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().destroy(request, *args, **kwargs)

    def create(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().create(request, *args, **kwargs)

    def list(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().list(request, *args, **kwargs)

    def retrieve(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().retrieve(request, *args, **kwargs)

    def update(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().update(request, *args, **kwargs)

    def partial_update(  # type: ignore[override] # pragma: no cover
        self, request: AnyBaseRequest, *args, **kwargs
    ):
        return super().partial_update(request, *args, **kwargs)

    # pylint: enable=useless-parent-delegation


# pylint: disable-next=too-many-ancestors
class ModelViewSet(
    BaseModelViewSet[
        Request[RequestUser],
        "ModelSerializer[RequestUser, AnyModel]",
        AnyModel,
    ],
    APIView[RequestUser],
    t.Generic[RequestUser, AnyModel],
):
    """Base model view set for all model view sets."""

    REQUIRED_ATTRS: t.Set[str] = {
        "request_class",
        "request_user_class",
        "model_class",
    }

    def get_bulk_queryset(self, lookup_values: t.Collection):
        """Get the queryset for a bulk action.

        Args:
            lookup_values: The values of the model's lookup field.

        Returns:
            A queryset containing the matching models.
        """
        return self.get_queryset().filter(
            **{f"{self.lookup_field}__in": lookup_values}
        )

    def bulk_create(self, request: Request[RequestUser]):
        """Bulk create many instances of a model.

        This is an extension of the default create action:
        https://www.django-rest-framework.org/api-guide/generic-views/#createmodelmixin

        Args:
            request: A HTTP request containing a list of models to create.

        Returns:
            A HTTP response containing a list of created models.
        """
        serializer = t.cast(
            "ModelListSerializer[RequestUser, AnyModel]",
            self.get_serializer(data=request.data, many=True),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )

    def perform_bulk_create(
        self, serializer: "ModelListSerializer[RequestUser, AnyModel]"
    ):
        """Bulk create many instances of a model.

        Args:
            serializer: A model serializer for the specific model.
        """
        serializer.save()

    def bulk_partial_update(self, request: Request[RequestUser]):
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
        queryset = self.get_bulk_queryset(request.json_dict.keys())
        serializer = t.cast(
            "ModelListSerializer[RequestUser, AnyModel]",
            self.get_serializer(
                queryset,
                data=request.data,
                many=True,
                partial=True,
            ),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)

    def perform_bulk_update(
        self, serializer: "ModelListSerializer[RequestUser, AnyModel]"
    ):
        """Partially bulk update many instances of a model.

        Args:
            serializer: A model serializer for the specific model.
        """
        serializer.save()

    def bulk_destroy(self, request: Request[RequestUser]):
        """Bulk destroy many instances of a model.

        This is an extension of the default destroy action:
        https://www.django-rest-framework.org/api-guide/generic-views/#destroymodelmixin

        Args:
            request: A HTTP request containing a list of models to destroy.

        Returns:
            A HTTP response containing a list of destroyed models.
        """
        queryset = self.get_bulk_queryset(request.data)
        self.perform_bulk_destroy(queryset)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, queryset: QuerySet[AnyModel]):
        """Bulk destroy many instances of a model.

        Args:
            queryset: A queryset of the models to delete.
        """
        queryset.delete()

    @action(detail=False, methods=["post", "patch", "delete"])
    def bulk(self, request: Request[RequestUser]):
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

    @staticmethod
    def _update_action(
        name: str,
        serializer_kwargs: t.Optional[KwArgs],
        response_kwargs: t.Optional[KwArgs],
        get_instance: t.Callable[
            ["ModelViewSet[RequestUser, AnyModel]", Request[RequestUser]],
            t.Union[AnyModel, t.Iterable[AnyModel]],
        ],
        detail: bool,
        **kwargs,
    ):
        def update(
            self: ModelViewSet[RequestUser, AnyModel],
            request: Request[RequestUser],
            **_: str,
        ):
            instance = get_instance(self, request)
            serializer = self.get_serializer(
                **(serializer_kwargs or {}),
                instance=instance,
                data=request.data,
                many=not detail,
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(**(response_kwargs or {}), data=serializer.data)

        update.__name__ = name

        return action(**kwargs, detail=detail, methods=["put"])(update)

    @classmethod
    def update_action(
        cls,
        name: str,
        serializer_kwargs: t.Optional[KwArgs] = None,
        response_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        """Generate a update action.

        Example usage:

        class UserViewSet(ModelViewSet[User]):
            rename = ModelViewSet.update_action(name="rename")

        Args:
            name: The action's function's name.
            serializer_kwargs: The kwargs to initialize to the serializer.
            response_kwargs: The kwargs to initialize to the response.

        Returns:
            A named update action.
        """

        return cls._update_action(
            name=name,
            serializer_kwargs=serializer_kwargs,
            response_kwargs=response_kwargs,
            get_instance=lambda self, _: self.get_object(),
            detail=True,
            **kwargs,
        )

    @classmethod
    def bulk_update_action(
        cls,
        name: str,
        serializer_kwargs: t.Optional[KwArgs] = None,
        response_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        """Generate a bulk-update action.

        Example usage:

        class UserViewSet(ModelViewSet[User]):
            rename = ModelViewSet.bulk_update_action(name="rename")

        Args:
            name: The action's function's name.
            serializer_kwargs: The kwargs to initialize to the serializer.
            response_kwargs: The kwargs to initialize to the response.

        Returns:
            A named bulk-update action.
        """

        return cls._update_action(
            name=name,
            serializer_kwargs=serializer_kwargs,
            response_kwargs=response_kwargs,
            get_instance=lambda self, request: self.get_bulk_queryset(
                request.json_dict.keys()
            ),
            detail=False,
            **kwargs,
        )
