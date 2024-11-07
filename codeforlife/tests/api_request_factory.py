"""
© Ocado Group
Created on 08/02/2024 at 15:42:25(+00:00).
"""

import typing as t

from django.contrib.auth.models import AbstractBaseUser
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.test import APIRequestFactory as _APIRequestFactory

from ..request import BaseRequest, Request
from ..types import get_arg

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    AnyUser = t.TypeVar("AnyUser", bound=User)
else:
    AnyUser = t.TypeVar("AnyUser")

AnyBaseRequest = t.TypeVar("AnyBaseRequest", bound=BaseRequest)
AnyAbstractBaseUser = t.TypeVar("AnyAbstractBaseUser", bound=AbstractBaseUser)
# pylint: enable=duplicate-code


class BaseAPIRequestFactory(
    _APIRequestFactory, t.Generic[AnyBaseRequest, AnyAbstractBaseUser]
):
    """Custom API request factory that returns DRF's Request object."""

    def _init_request(self, wsgi_request: WSGIRequest):
        return t.cast(
            AnyBaseRequest,
            BaseRequest(
                wsgi_request,
                parsers=[
                    JSONParser(),
                    FormParser(),
                    MultiPartParser(),
                    FileUploadParser(),
                ],
            ),
        )

    def request(self, user: t.Optional[AnyAbstractBaseUser] = None, **kwargs):
        wsgi_request = t.cast(WSGIRequest, super().request(**kwargs))
        request = self._init_request(wsgi_request)
        if user:
            # pylint: disable-next=attribute-defined-outside-init
            request.user = user

        return request

    # pylint: disable-next=too-many-arguments
    def generic(
        self,
        method: str,
        path: t.Optional[str] = None,
        data: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        secure: bool = True,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        return t.cast(
            AnyBaseRequest,
            super().generic(
                method,
                path or "/",
                data or "",
                content_type or "application/json",
                secure,
                user=user,
                **extra,
            ),
        )

    def get(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Any = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        return t.cast(
            AnyBaseRequest,
            super().get(
                path or "/",
                data,
                user=user,
                **extra,
            ),
        )

    # pylint: disable-next=too-many-arguments
    def post(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Any = None,
        # pylint: disable-next=redefined-builtin
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            AnyBaseRequest,
            super().post(
                path or "/",
                data,
                format,
                content_type,
                user=user,
                **extra,
            ),
        )

    # pylint: disable-next=too-many-arguments
    def put(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Any = None,
        # pylint: disable-next=redefined-builtin
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            AnyBaseRequest,
            super().put(
                path or "/",
                data,
                format,
                content_type,
                user=user,
                **extra,
            ),
        )

    # pylint: disable-next=too-many-arguments
    def patch(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Any = None,
        # pylint: disable-next=redefined-builtin
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            AnyBaseRequest,
            super().patch(
                path or "/",
                data,
                format,
                content_type,
                user=user,
                **extra,
            ),
        )

    # pylint: disable-next=too-many-arguments
    def delete(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Any = None,
        # pylint: disable-next=redefined-builtin
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            AnyBaseRequest,
            super().delete(
                path or "/",
                data,
                format,
                content_type,
                user=user,
                **extra,
            ),
        )

    # pylint: disable-next=too-many-arguments
    def options(  # type: ignore[override]
        self,
        path: t.Optional[str] = None,
        data: t.Optional[t.Union[t.Dict[str, str], str]] = None,
        # pylint: disable-next=redefined-builtin
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        user: t.Optional[AnyAbstractBaseUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            AnyBaseRequest,
            super().options(
                path or "/",
                data or {},
                format,
                content_type,
                user=user,
                **extra,
            ),
        )


class APIRequestFactory(
    BaseAPIRequestFactory[Request[AnyUser], AnyUser],
    t.Generic[AnyUser],
):
    """Custom API request factory that returns DRF's Request object."""

    def __init__(self, user_class: t.Type[AnyUser], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_class = user_class

    @classmethod
    def get_user_class(cls) -> t.Type[AnyUser]:
        """Get the user class.

        Returns:
            The user class.
        """
        return get_arg(cls, 0)

    def _init_request(self, wsgi_request):
        return Request[AnyUser](
            self.user_class,
            wsgi_request,
            parsers=[
                JSONParser(),
                FormParser(),
                MultiPartParser(),
                FileUploadParser(),
            ],
        )
