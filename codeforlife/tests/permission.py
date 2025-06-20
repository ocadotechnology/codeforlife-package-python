"""
© Ocado Group
Created on 19/06/2025 at 11:30:00(+00:00).
"""

import typing as t

from rest_framework.request import Request
from rest_framework.views import APIView

from ..permissions import BasePermission
from ..types import Args, KwArgs
from .api_request_factory import APIRequestFactory, BaseAPIRequestFactory
from .test import TestCase

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
else:
    RequestUser = t.TypeVar("RequestUser")

AnyBasePermission = t.TypeVar("AnyBasePermission", bound=BasePermission)
AnyBaseAPIRequestFactory = t.TypeVar(
    "AnyBaseAPIRequestFactory", bound=BaseAPIRequestFactory
)
# pylint: enable=duplicate-code


class BasePermissionTestCase(
    TestCase,
    t.Generic[AnyBasePermission, AnyBaseAPIRequestFactory],
):
    """Base test case for all permission test cases."""

    permission_class: t.Type[AnyBasePermission]
    request_factory_class: t.Type[AnyBaseAPIRequestFactory]
    request_factory: AnyBaseAPIRequestFactory

    REQUIRED_ATTRS: t.Set[str] = {"permission_class", "request_factory_class"}

    @classmethod
    def _initialize_request_factory(cls):
        return cls.request_factory_class()

    @classmethod
    def setUpClass(cls):
        for attr in cls.REQUIRED_ATTRS:
            assert hasattr(cls, attr), f'Attribute "{attr}" must be set.'

        cls.request_factory = cls._initialize_request_factory()

        return super().setUpClass()

    def assert_eq(
        self,
        args1: t.Optional[Args] = None,
        kwargs1: t.Optional[KwArgs] = None,
        args2: t.Optional[Args] = None,
        kwargs2: t.Optional[KwArgs] = None,
    ):
        """Assert the __eq__ operator correctly equates two instances.

        NOTE: The args for 1 and 2 should be different!

        Args:
            args1: The args to initialize the first instance.
            kwargs1: The kwargs to initialize the first instance.
            args2: The args to initialize the second instance.
            kwargs2: The kwargs to initialize the second instance.
        """
        args1, kwargs1 = args1 or tuple(), kwargs1 or {}
        args2, kwargs2 = args2 or tuple(), kwargs2 or {}

        permission1 = self.permission_class(*args1, **kwargs1)
        permission2 = self.permission_class(*args2, **kwargs2)

        # Assert permissions equal with the same args.
        assert permission1 == self.permission_class(*args1, **kwargs1)
        assert permission2 == self.permission_class(*args2, **kwargs2)

        # Assert permissions do not equal with different args.
        assert permission1 != permission2

        # Assert that child class is not the same as parent.
        base_permission = BasePermission()
        assert permission1 != base_permission
        assert permission2 != base_permission

    def assert_has_permission(
        self,
        has_permission: bool,
        request: Request,
        *args,
        view: APIView = APIView(),
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Assert whether or not the request has permission to call the view.

        Args:
            has_permission: A flag designating whether the request has permission.
            request: The request to grant permission to.
            view: The view to grant permission to.
        """
        # pylint: enable=line-too-long
        permission = self.permission_class(*args, **kwargs)
        assert has_permission == permission.has_permission(request, view)


class PermissionTestCase(
    BasePermissionTestCase[AnyBasePermission, APIRequestFactory[RequestUser]],
    t.Generic[AnyBasePermission, RequestUser],
):
    """Base test case for all permission test cases."""

    request_factory_class = APIRequestFactory
    request_user_class: t.Type[RequestUser]

    REQUIRED_ATTRS = {
        *BasePermissionTestCase.REQUIRED_ATTRS,
        "request_user_class",
    }

    @classmethod
    def _initialize_request_factory(cls):
        return cls.request_factory_class(cls.request_user_class)
