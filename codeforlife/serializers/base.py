"""
© Ocado Group
Created on 29/01/2024 at 14:27:09(+00:00).

Base serializer.
"""

import typing as t

from django.views import View
from rest_framework.serializers import BaseSerializer as _BaseSerializer

from ..request import BaseRequest

# pylint: disable=duplicate-code
AnyBaseRequest = t.TypeVar("AnyBaseRequest", bound=BaseRequest)
# pylint: enable=duplicate-code


# pylint: disable-next=abstract-method
class BaseSerializer(_BaseSerializer, t.Generic[AnyBaseRequest]):
    """Base serializer to be inherited by all other serializers."""

    @property
    def request(self):
        """The HTTP request that triggered the view."""

        return t.cast(AnyBaseRequest, self.context["request"])

    @property
    def view(self):
        """The view that instantiated this serializer."""

        return t.cast(View, self.context["view"])
