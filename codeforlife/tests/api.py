"""
© Ocado Group
Created on 23/02/2024 at 08:46:27(+00:00).
"""

import typing as t

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

    REQUIRED_ATTRS: t.Set[str] = {"client_class"}

    @classmethod
    def setUpClass(cls):
        for attr in cls.REQUIRED_ATTRS:
            assert hasattr(cls, attr), f'Attribute "{attr}" must be set.'

        return super().setUpClass()

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
    request_user_class: t.Type[RequestUser]

    REQUIRED_ATTRS: t.Set[str] = {"client_class", "request_user_class"}
