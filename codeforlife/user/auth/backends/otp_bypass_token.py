import typing as t

from django.contrib.auth.backends import BaseBackend
from django.http.request import HttpRequest

from ...models import AuthFactor, User


class OtpBypassTokenBackend(BaseBackend):
    """Authenticates if the OTP bypass token belongs to the identified user."""

    def authenticate(
        self,
        request: t.Optional[HttpRequest],
        token: t.Optional[str] = None,
        **kwargs,
    ):
        if (
            request is None
            or token is None
            or not isinstance(request.user, User)
            or not request.user.session.session_auth_factors.filter(
                auth_factor__type=AuthFactor.Type.OTP
            ).exists()
        ):
            return None

        for otp_bypass_token in request.user.otp_bypass_tokens.all():
            if otp_bypass_token.check_token(token):
                # Delete OTP auth factor from session.
                request.user.session.session_auth_factors.filter(
                    auth_factor__type=AuthFactor.Type.OTP
                ).delete()

                return request.user

        return None

    def get_user(self, user_id: int):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
