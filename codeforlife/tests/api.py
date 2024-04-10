"""
© Ocado Group
Created on 23/02/2024 at 08:46:27(+00:00).
"""

import json
import typing as t
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient as _APIClient
from rest_framework.test import APITestCase as _APITestCase

from ..types import DataDict, JsonDict
from ..user.models import AdminSchoolTeacherUser
from ..user.models import AnyUser as RequestUser
from ..user.models import (
    AuthFactor,
    IndependentUser,
    NonAdminSchoolTeacherUser,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    StudentUser,
    TeacherUser,
    TypedUser,
    User,
)
from .api_request_factory import APIRequestFactory

LoginUser = t.TypeVar("LoginUser", bound=User)


class APIClient(_APIClient, t.Generic[RequestUser]):
    """Base API client to be inherited by all other API clients."""

    _test_case: "APITestCase[RequestUser]"

    def __init__(self, enforce_csrf_checks: bool = False, **defaults):
        super().__init__(enforce_csrf_checks, **defaults)

        # pylint: disable-next=too-few-public-methods
        class _APIRequestFactory(
            APIRequestFactory[  # type: ignore[misc]
                self.get_request_user_class()
            ]
        ):
            pass

        self.request_factory = _APIRequestFactory(
            enforce_csrf_checks,
            **defaults,
        )

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
    # Login Helpers
    # --------------------------------------------------------------------------

    def _login_user_type(self, user_type: t.Type[LoginUser], **credentials):
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
                    request=self.request_factory.post(user=user),
                    otp=otp,
                ), f'Failed to login with OTP "{otp}" at {now}.'

        assert user.is_authenticated, "Failed to authenticate user."

        return user

    def login(self, **credentials):
        """Log in a user.

        Returns:
            The user.
        """
        return self._login_user_type(User, **credentials)

    def login_teacher(self, email: str, password: str = "password"):
        """Log in a user and assert they are a teacher.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The teacher-user.
        """
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
        return self._login_user_type(
            IndependentUser, email=email, password=password
        )

    def login_as(self, user: TypedUser, password: str = "password"):
        """Log in as a user. The user instance needs to be a user proxy in order
        to know which credentials are required.

        Args:
            user: The user to log in as.
            password: The user's password.
        """
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
            "\nValidation errors:: "
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


class APITestCase(_APITestCase, t.Generic[RequestUser]):
    """Base API test case to be inherited by all other API test cases."""

    client: APIClient[RequestUser]
    client_class: t.Type[APIClient[RequestUser]] = APIClient

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

    def _get_client_class(self):
        # pylint: disable-next=too-few-public-methods
        class _Client(
            self.client_class[  # type: ignore[misc]
                self.get_request_user_class()
            ]
        ):
            _test_case = self

        return _Client

    def _pre_setup(self):
        self.client_class = self._get_client_class()
        super()._pre_setup()  # type: ignore[misc]
