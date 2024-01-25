"""
© Ocado Group
Created on 24/01/2024 at 13:08:23(+00:00).
"""

import typing as t

from django.db.models import Model
from rest_framework.viewsets import ModelViewSet as DrfModelViewSet

from ..serializers import ModelSerializer

AnyModel = t.TypeVar("AnyModel", bound=Model)


# pylint: disable-next=too-few-public-methods
class _ModelViewSet(t.Generic[AnyModel]):
    pass


if t.TYPE_CHECKING:
    # pylint: disable-next=too-few-public-methods
    class ModelViewSet(
        DrfModelViewSet[AnyModel],
        _ModelViewSet[AnyModel],
        t.Generic[AnyModel],
    ):
        """Base model view set for all model view sets."""

        serializer_class: t.Optional[t.Type[ModelSerializer[AnyModel]]]

else:
    # pylint: disable-next=missing-class-docstring,too-many-ancestors
    class ModelViewSet(
        DrfModelViewSet,
        _ModelViewSet[AnyModel],
        t.Generic[AnyModel],
    ):
        pass
