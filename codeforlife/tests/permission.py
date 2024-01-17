"""
© Ocado Group
Created on 15/01/2024 at 15:15:20(+00:00).

Test helpers for Django Rest Framework permissions.
"""

import typing as t

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from ..permissions import AnyPermission
from ..types import Args, KwArgs


class PermissionTestCase(TestCase, t.Generic[AnyPermission]):
    """Base for all permission test cases."""

    @classmethod
    def get_permission_class(cls) -> t.Type[AnyPermission]:
        """Get the permission's class.

        Returns:
            The permission's class.
        """

        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

    def setUp(self):
        self.request_factory = APIRequestFactory()

    def _has_permission(
        self,
        request: Request,
        view: t.Optional[APIView],
        init_args: t.Optional[Args],
        init_kwargs: t.Optional[KwArgs],
    ):
        view = view or APIView()
        init_args = init_args or tuple()
        init_kwargs = init_kwargs or {}

        permission_class = self.get_permission_class()
        permission = permission_class(*init_args, **init_kwargs)
        return permission.has_permission(request, view)

    def assert_has_permission(
        self,
        request: Request,
        view: t.Optional[APIView] = None,
        init_args: t.Optional[Args] = None,
        init_kwargs: t.Optional[KwArgs] = None,
    ):
        """Assert that the request does have permission.

        Args:
            request: The request being sent to the view.
            view: The view that is being requested.
            init_args: The arguments used to initialize the permission.
            init_kwargs: The keyword arguments used to initialize the
                permission.
        """

        assert self._has_permission(
            request,
            view,
            init_args,
            init_kwargs,
        )

    def assert_not_has_permission(
        self,
        request: Request,
        view: t.Optional[APIView] = None,
        init_args: t.Optional[Args] = None,
        init_kwargs: t.Optional[KwArgs] = None,
    ):
        """Assert that the request does not have permission.

        Args:
            request: The request being sent to the view.
            view: The view that is being requested.
            init_args: The arguments used to initialize the permission.
            init_kwargs: The keyword arguments used to initialize the
                permission.
        """

        assert not self._has_permission(
            request,
            view,
            init_args,
            init_kwargs,
        )
