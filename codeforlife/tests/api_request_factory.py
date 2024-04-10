"""
© Ocado Group
Created on 08/02/2024 at 15:42:25(+00:00).
"""

import typing as t

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.parsers import (
    FileUploadParser,
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.test import APIRequestFactory as _APIRequestFactory

from ..request import Request
from ..user.models import AnyUser


class APIRequestFactory(_APIRequestFactory, t.Generic[AnyUser]):
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
        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

    def request(self, user: t.Optional[AnyUser] = None, **kwargs):
        wsgi_request = t.cast(WSGIRequest, super().request(**kwargs))

        request = Request(
            self.user_class,
            wsgi_request,
            parsers=[
                JSONParser(),
                FormParser(),
                MultiPartParser(),
                FileUploadParser(),
            ],
        )

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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            Request[AnyUser],
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
        user: t.Optional[AnyUser] = None,
        **extra
    ):
        if format is None and content_type is None:
            format = "json"

        return t.cast(
            Request[AnyUser],
            super().options(
                path or "/",
                data or {},
                format,
                content_type,
                user=user,
                **extra,
            ),
        )
