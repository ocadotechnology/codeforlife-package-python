"""
© Ocado Group
Created on 06/11/2024 at 13:35:13(+00:00).
"""

import json
import typing as t
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient as _APIClient

from ..types import DataDict, JsonDict
from .api_request_factory import APIRequestFactory, BaseAPIRequestFactory

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import TypedUser, User
    from .api import APITestCase, BaseAPITestCase

    RequestUser = t.TypeVar("RequestUser", bound=User)
    LoginUser = t.TypeVar("LoginUser", bound=User)
    AnyBaseAPITestCase = t.TypeVar("AnyBaseAPITestCase", bound=BaseAPITestCase)
else:
    RequestUser = t.TypeVar("RequestUser")
    LoginUser = t.TypeVar("LoginUser")
    AnyBaseAPITestCase = t.TypeVar("AnyBaseAPITestCase")

AnyBaseAPIRequestFactory = t.TypeVar(
    "AnyBaseAPIRequestFactory", bound=BaseAPIRequestFactory
)
# pylint: enable=duplicate-code


class BaseAPIClient(
    _APIClient,
    t.Generic[AnyBaseAPITestCase, AnyBaseAPIRequestFactory],
):
    """Base API client to be inherited by all other API clients."""

    _test_case: AnyBaseAPITestCase

    request_factory: AnyBaseAPIRequestFactory
    request_factory_class: t.Type[AnyBaseAPIRequestFactory]

    def _initialize_request_factory(
        self, enforce_csrf_checks: bool, **defaults
    ):
        return self.request_factory_class(enforce_csrf_checks, **defaults)

    def __init__(
        self,
        enforce_csrf_checks: bool = False,
        raise_request_exception=False,
        **defaults,
    ):
        super().__init__(
            enforce_csrf_checks,
            raise_request_exception=raise_request_exception,
            **defaults,
        )

        self.request_factory = self._initialize_request_factory(
            enforce_csrf_checks, **defaults
        )

    @staticmethod
    def status_code_is_ok(status_code: int):
        """Check if the status code is greater than or equal to 200 and less
        than 300.

        Args:
            status_code: The status code to check.

        Returns:
            A flag designating if the status code is OK.
        """
        return 200 <= status_code < 300

    # --------------------------------------------------------------------------
    # Assert Response Helpers
    # --------------------------------------------------------------------------

    def _assert_response(self, response: Response, make_assertions: t.Callable):
        if self.status_code_is_ok(response.status_code):
            make_assertions()

    def _assert_response_json(
        self,
        response: Response,
        make_assertions: t.Callable[[JsonDict], None],
    ):
        self._assert_response(
            response,
            make_assertions=lambda: make_assertions(
                response.json(),  # type: ignore[attr-defined]
            ),
        )

    def _assert_response_json_bulk(
        self,
        response: Response,
        make_assertions: t.Callable[[t.List[JsonDict]], None],
        data: t.List[DataDict],
    ):
        def _make_assertions():
            response_json = response.json()  # type: ignore[attr-defined]
            assert isinstance(response_json, list)
            assert len(response_json) == len(data)
            make_assertions(response_json)

        self._assert_response(response, _make_assertions)

    # --------------------------------------------------------------------------
    # Request Helpers
    # --------------------------------------------------------------------------

    StatusCodeAssertion = t.Optional[t.Union[int, t.Callable[[int], bool]]]

    # pylint: disable=too-many-arguments,redefined-builtin

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/json",
        secure=False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        response = t.cast(
            Response,
            super().generic(
                method,
                path,
                data,
                content_type,
                secure,
                **extra,
            ),
        )

        # Use a custom kwarg to handle the common case of checking the
        # response's status code.
        if status_code_assertion is None:
            status_code_assertion = self.status_code_is_ok
        elif isinstance(status_code_assertion, int):
            expected_status_code = status_code_assertion
            status_code_assertion = (
                # pylint: disable-next=unnecessary-lambda-assignment
                lambda status_code: status_code
                == expected_status_code
            )

        # pylint: disable-next=no-member
        status_code = response.status_code
        assert status_code_assertion(
            status_code
        ), f"Unexpected status code: {status_code}." + (
            "\nValidation errors: "
            + json.dumps(
                # pylint: disable-next=no-member
                response.json(),  # type: ignore[attr-defined]
                indent=2,
                default=str,
            )
            if status_code == status.HTTP_400_BAD_REQUEST
            else ""
        )

        return response

    def get(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        return super().get(
            path=path,
            data=data,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    def post(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        if format is None and content_type is None:
            format = "json"

        return super().post(
            path=path,
            data=data,
            format=format,
            content_type=content_type,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    def put(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        if format is None and content_type is None:
            format = "json"

        return super().put(
            path=path,
            data=data,
            format=format,
            content_type=content_type,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    def patch(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        if format is None and content_type is None:
            format = "json"

        return super().patch(
            path=path,
            data=data,
            format=format,
            content_type=content_type,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    def delete(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        if format is None and content_type is None:
            format = "json"

        return super().delete(
            path=path,
            data=data,
            format=format,
            content_type=content_type,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    def options(  # type: ignore[override]
        self,
        path: str,
        data: t.Any = None,
        format: t.Optional[str] = None,
        content_type: t.Optional[str] = None,
        follow: bool = False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        if format is None and content_type is None:
            format = "json"

        return super().options(
            path=path,
            data=data,
            format=format,
            content_type=content_type,
            follow=follow,
            status_code_assertion=status_code_assertion,
            **extra,
        )

    # pylint: enable=too-many-arguments,redefined-builtin


class APIClient(
    BaseAPIClient["APITestCase[RequestUser]", APIRequestFactory[RequestUser]],
    t.Generic[RequestUser],
):
    """Base API client to be inherited by all other API clients."""

    request_factory_class = APIRequestFactory

    @property
    def request_user_class(self) -> t.Type[RequestUser]:
        """Shorthand to access generic user class."""
        return self._test_case.request_user_class

    def _initialize_request_factory(self, enforce_csrf_checks, **defaults):
        return self.request_factory_class(
            self.request_user_class,
            enforce_csrf_checks,
            **defaults,
        )

    # --------------------------------------------------------------------------
    # Login Helpers
    # --------------------------------------------------------------------------

    def _login_user_type(self, user_type: t.Type[LoginUser], **credentials):
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import AuthFactor

        # Logout current user (if any) before logging in next user.
        self.logout()
        assert super().login(
            **credentials
        ), f"Failed to login with credentials: {credentials}."

        user = user_type.objects.get(session=self.session.session_key)

        if user.session.auth_factors.filter(
            auth_factor__type=AuthFactor.Type.OTP
        ).exists():
            now = timezone.now()
            otp = user.totp.at(now)
            with patch.object(timezone, "now", return_value=now):
                assert super().login(
                    request=self.request_factory.post(
                        user=t.cast(RequestUser, user)
                    ),
                    otp=otp,
                ), f'Failed to login with OTP "{otp}" at {now}.'

        assert user.is_authenticated, "Failed to authenticate user."

        return user

    def login(self, **credentials):
        """Log in a user.

        Returns:
            The user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import User

        return self._login_user_type(User, **credentials)

    def login_teacher(self, email: str, password: str = "password"):
        """Log in a user and assert they are a teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The teacher-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import TeacherUser

        return self._login_user_type(
            TeacherUser, email=email, password=password
        )

    def login_school_teacher(self, email: str, password: str = "password"):
        """Log in a user and assert they are a school-teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The school-teacher-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import SchoolTeacherUser

        return self._login_user_type(
            SchoolTeacherUser, email=email, password=password
        )

    def login_admin_school_teacher(
        self, email: str, password: str = "password"
    ):
        """Log in a user and assert they are an admin-school-teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The admin-school-teacher-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import AdminSchoolTeacherUser

        return self._login_user_type(
            AdminSchoolTeacherUser, email=email, password=password
        )

    def login_non_admin_school_teacher(
        self, email: str, password: str = "password"
    ):
        """Log in a user and assert they are a non-admin-school-teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The non-admin-school-teacher-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import NonAdminSchoolTeacherUser

        return self._login_user_type(
            NonAdminSchoolTeacherUser, email=email, password=password
        )

    def login_non_school_teacher(self, email: str, password: str = "password"):
        """Log in a user and assert they are a non-school-teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The non-school-teacher-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import NonSchoolTeacherUser

        return self._login_user_type(
            NonSchoolTeacherUser, email=email, password=password
        )

    def login_student(
        self, class_id: str, first_name: str, password: str = "password"
    ):
        """Log in a user and assert they are a student.

        Args:
            class_id: The ID of the class the student belongs to.
            first_name: The user's first name.
            password: The user's password.

        Returns:
            The student-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import StudentUser

        return self._login_user_type(
            StudentUser,
            first_name=first_name,
            password=password,
            class_id=class_id,
        )

    def login_indy(self, email: str, password: str = "password"):
        """Log in a user and assert they are an independent.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The independent-user.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import IndependentUser

        return self._login_user_type(
            IndependentUser, email=email, password=password
        )

    def login_as(self, user: "TypedUser", password: str = "password"):
        """Log in as a user. The user instance needs to be a user proxy in order
        to know which credentials are required.

        Args:
            user: The user to log in as.
            password: The user's password.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import (
            AdminSchoolTeacherUser,
            IndependentUser,
            NonAdminSchoolTeacherUser,
            NonSchoolTeacherUser,
            SchoolTeacherUser,
            StudentUser,
            TeacherUser,
        )

        auth_user = None

        if isinstance(user, AdminSchoolTeacherUser):
            auth_user = self.login_admin_school_teacher(user.email, password)
        elif isinstance(user, NonAdminSchoolTeacherUser):
            auth_user = self.login_non_admin_school_teacher(
                user.email, password
            )
        elif isinstance(user, SchoolTeacherUser):
            auth_user = self.login_school_teacher(user.email, password)
        elif isinstance(user, NonSchoolTeacherUser):
            auth_user = self.login_non_school_teacher(user.email, password)
        elif isinstance(user, TeacherUser):
            auth_user = self.login_teacher(user.email, password)
        elif isinstance(user, StudentUser):
            auth_user = self.login_student(
                user.student.class_field.access_code,
                user.first_name,
                password,
            )
        elif isinstance(user, IndependentUser):
            auth_user = self.login_indy(user.email, password)

        assert user == auth_user
