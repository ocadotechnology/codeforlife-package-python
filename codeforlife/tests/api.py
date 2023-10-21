import typing as t
from unittest.mock import patch

from pyotp import TOTP
from django.utils import timezone
from rest_framework.test import APITestCase as _APITestCase
from rest_framework.test import APIClient as _APIClient

from ..user.models import User, AuthFactor


class APIClient(_APIClient):
    StatusCodeAssertion = t.Optional[t.Union[int, t.Callable[[int], bool]]]

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        wsgi_response = super().generic(
            method, path, data, content_type, secure, **extra
        )

        # Use a custom kwarg to handle the common case of checking the
        # response's status code.
        if status_code_assertion is None:
            status_code_assertion = (
                lambda status_code: 200 <= status_code <= 299
            )
        elif isinstance(status_code_assertion, int):
            expected_status_code = status_code_assertion
            status_code_assertion = (
                lambda status_code: status_code == expected_status_code
            )
        assert status_code_assertion(
            wsgi_response.status_code
        ), f"Response has error status code: {wsgi_response.status_code}"

        return wsgi_response

    def login(self, **credentials):
        assert super().login(
            **credentials
        ), f"Failed to login with credentials: {credentials}"

        user = User.objects.get(session=self.session.session_key)

        if user.session.session_auth_factors.filter(
            auth_factor__type=AuthFactor.Type.OTP
        ).exists():
            now = timezone.now()
            otp = TOTP(user.otp_secret).at(now)
            with patch.object(timezone, "now", return_value=now):
                assert super().login(
                    otp=otp
                ), f'Failed to login with OTP "{otp}" at {now}'

        assert user.is_authenticated, "Failed to authenticate user."

        return user


class APITestCase(_APITestCase):
    client: APIClient
    client_class = APIClient
