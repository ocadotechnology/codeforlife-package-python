"""
© Ocado Group
Created on 05/02/2024 at 16:33:52(+00:00).
"""

import typing as t

from django.http import HttpRequest
from rest_framework.views import APIView as _APIView

from ..request import BaseRequest, Request

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
else:
    RequestUser = t.TypeVar("RequestUser")

AnyBaseRequest = t.TypeVar("AnyBaseRequest", bound=BaseRequest)

# pylint: enable=duplicate-code


# pylint: disable-next=missing-class-docstring
class BaseAPIView(_APIView, t.Generic[AnyBaseRequest]):
    request: AnyBaseRequest
    request_class: t.Type[AnyBaseRequest]

    REQUIRED_ATTRS: t.Set[str] = {"request_class"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for attr in self.REQUIRED_ATTRS:
            assert hasattr(self, attr), f'Attribute "{attr}" must be set.'

    def _initialize_request(self, request: HttpRequest, **kwargs):
        kwargs["request"] = request
        kwargs.setdefault("parsers", self.get_parsers())
        kwargs.setdefault("authenticators", self.get_authenticators())
        kwargs.setdefault("negotiator", self.get_content_negotiator())
        kwargs.setdefault("parser_context", self.get_parser_context(request))

        return self.request_class(**kwargs)

    def initialize_request(self, request, *args, **kwargs):
        # NOTE: Call to super has side effects and is required.
        super().initialize_request(request, *args, **kwargs)

        return self._initialize_request(request)


# pylint: disable-next=missing-class-docstring
class APIView(BaseAPIView[Request[RequestUser]], t.Generic[RequestUser]):
    request_class = Request
    request_user_class: t.Type[RequestUser]

    REQUIRED_ATTRS: t.Set[str] = {"request_class", "request_user_class"}

    def _initialize_request(self, request, **kwargs):
        kwargs["user_class"] = self.request_user_class
        return super()._initialize_request(request, **kwargs)
