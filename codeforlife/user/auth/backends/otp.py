"""
© Ocado Group
Created on 01/02/2024 at 14:41:20(+00:00).
"""

import typing as t

from django.utils import timezone

from ....request import HttpRequest
from ...models import AuthFactor
from .base import BaseBackend


class OtpBackend(BaseBackend):
    """Check a user's multi-factor OTP authentication."""

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        otp: t.Optional[str] = None,
        **kwargs,
    ):
        # Avoid near misses by getting the timestamp before any processing.
        now = timezone.now()

        if (
            otp is None
            or request is None
            or not isinstance(request.user, self.user_class)
            or not request.user.userprofile.otp_secret
            or not request.user.session.auth_factors.filter(
                auth_factor__type=AuthFactor.Type.OTP
            ).exists()
        ):
            return None

        user = request.user

        # Verify the otp is valid for now.
        if user.totp.verify(otp, for_time=now):
            # Deny replay attacks by rejecting the otp for last time.
            last_otp_for_time = user.userprofile.last_otp_for_time
            if last_otp_for_time and user.totp.verify(otp, last_otp_for_time):
                return None
            user.userprofile.last_otp_for_time = now
            user.userprofile.save()

            # Delete OTP auth factor from session.
            user.session.auth_factors.filter(
                auth_factor__type=AuthFactor.Type.OTP
            ).delete()

            return user

        return None
