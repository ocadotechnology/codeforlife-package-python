"""
© Ocado Group
Created on 23/02/2024 at 08:46:27(+00:00).
"""

import typing as t

from ..types import get_arg
from .api_client import APIClient, BaseAPIClient
from .test import TestCase

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User

    RequestUser = t.TypeVar("RequestUser", bound=User)
else:
    RequestUser = t.TypeVar("RequestUser")

AnyBaseAPIClient = t.TypeVar("AnyBaseAPIClient", bound=BaseAPIClient)
# pylint: enable=duplicate-code


class BaseAPITestCase(TestCase, t.Generic[AnyBaseAPIClient]):
    """Base API test case to be inherited by all other API test cases."""

    client: AnyBaseAPIClient
    client_class: t.Type[AnyBaseAPIClient]

    def _pre_setup(self):
        # pylint: disable-next=protected-access
        self.client_class._test_case = self
        super()._pre_setup()  # type: ignore[misc]


class APITestCase(
    BaseAPITestCase[APIClient[RequestUser]],
    t.Generic[RequestUser],
):
    """Base API test case to be inherited by all other API test cases."""

    client_class = APIClient

    @classmethod
    def get_request_user_class(cls) -> t.Type[RequestUser]:
        """Get the request's user class.

        Returns:
            The request's user class.
        """
        return get_arg(cls, 0)

    def _get_client_class(self):
        # pylint: disable-next=too-few-public-methods
        class _Client(
            self.client_class[  # type: ignore[misc]
                self.get_request_user_class()
            ]
        ):
            pass

        return _Client

    def _pre_setup(self):
        self.client_class = self._get_client_class()
        super()._pre_setup()
