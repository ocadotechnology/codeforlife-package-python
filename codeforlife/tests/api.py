import typing as t
from unittest.mock import patch

from pyotp import TOTP
from django.urls import reverse
from django.utils import timezone
from django.db.models import Model
from rest_framework.test import APITestCase as _APITestCase
from rest_framework.test import APIClient as _APIClient
from rest_framework.serializers import BaseSerializer
from rest_framework.response import Response

from ..user.models import User, AuthFactor


AnySerializer = t.TypeVar("AnySerializer", bound=BaseSerializer)
AnyModel = t.TypeVar("AnyModel", bound=Model)


class APIClient(_APIClient):
    StatusCodeAssertion = t.Optional[t.Union[int, t.Callable[[int], bool]]]

    @staticmethod
    def status_code_is_ok(status_code: int):
        return 200 <= status_code < 300

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
            status_code_assertion = self.status_code_is_ok
        elif isinstance(status_code_assertion, int):
            expected_status_code = status_code_assertion
            status_code_assertion = (
                lambda status_code: status_code == expected_status_code
            )
        assert status_code_assertion(
            wsgi_response.status_code
        ), f"Unexpected status code: {wsgi_response.status_code}."

        return wsgi_response

    def login(self, **credentials):
        assert super().login(
            **credentials
        ), f"Failed to login with credentials: {credentials}."

        user = User.objects.get(session=self.session.session_key)

        if user.session.session_auth_factors.filter(
            auth_factor__type=AuthFactor.Type.OTP
        ).exists():
            now = timezone.now()
            otp = TOTP(user.otp_secret).at(now)
            with patch.object(timezone, "now", return_value=now):
                assert super().login(
                    otp=otp
                ), f'Failed to login with OTP "{otp}" at {now}.'

        assert user.is_authenticated, "Failed to authenticate user."

        return user

    @staticmethod
    def assert_data_equals_model(
        data: t.Dict[str, t.Any],
        model: AnyModel,
        serializer_class: t.Type[AnySerializer],
    ):
        assert (
            data == serializer_class(model).data
        ), "Data does not equal serialized model."

    def retrieve(
        self,
        basename: str,
        model: AnyModel,
        serializer_class: t.Type[AnySerializer],
        status_code_assertion: StatusCodeAssertion = None,
        **kwargs,
    ):
        response: Response = self.get(
            reverse(f"{basename}-detail", kwargs={"pk": model.pk}),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if self.status_code_is_ok(response.status_code):
            self.assert_data_equals_model(
                response.json(),
                model,
                serializer_class,
            )

        return response

    def list(
        self,
        basename: str,
        models: t.Iterable[AnyModel],
        serializer_class: t.Type[AnySerializer],
        status_code_assertion: StatusCodeAssertion = None,
        **kwargs,
    ):
        response: Response = self.get(
            reverse(f"{basename}-list"),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if self.status_code_is_ok(response.status_code):
            for data, model in zip(response.json()["data"], models):
                self.assert_data_equals_model(
                    data,
                    model,
                    serializer_class,
                )

        return response


class APITestCase(_APITestCase):
    client: APIClient
    client_class = APIClient
