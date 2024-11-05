"""
© Ocado Group
Created on 05/02/2024 at 16:33:52(+00:00).
"""

import typing as t

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


# pylint: disable-next=missing-class-docstring
class APIView(BaseAPIView[Request[RequestUser]], t.Generic[RequestUser]):
    @classmethod
    def get_request_user_class(cls) -> t.Type[RequestUser]:
        """Get the request's user class.

        Returns:
            The request's user class.
        """
        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

    def initialize_request(self, request, *args, **kwargs):
        # NOTE: Call to super has side effects and is required.
        super().initialize_request(request, *args, **kwargs)

        return Request(
            user_class=self.get_request_user_class(),
            request=request,
            parsers=self.get_parsers(),
            authenticators=self.get_authenticators(),
            negotiator=self.get_content_negotiator(),
            parser_context=self.get_parser_context(request),
        )
