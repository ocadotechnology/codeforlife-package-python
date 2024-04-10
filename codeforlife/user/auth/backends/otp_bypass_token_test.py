"""
© Ocado Group
Created on 10/04/2024 at 13:17:18(+01:00).
"""

from datetime import timedelta

from django.utils import timezone

from ....tests import APIRequestFactory, TestCase
from ...models import (
    AuthFactor,
    OtpBypassToken,
    Session,
    SessionAuthFactor,
    User,
)
from .otp_bypass_token import OtpBypassTokenBackend


# pylint: disable-next=missing-class-docstring,too-many-instance-attributes
class TestTokenBackend(TestCase):
    def setUp(self):
        self.backend = OtpBypassTokenBackend()
        self.request_factory = APIRequestFactory(User)

        self.user = User.objects.get(id=2)

        self.auth_factor = AuthFactor.objects.create(
            user=self.user,
            type=AuthFactor.Type.OTP,
        )

        self.session = Session.objects.create(
            session_key="a",
            session_data="",
            expire_date=timezone.now() + timedelta(hours=24),
            user=self.user,
        )

        self.session_auth_factor = SessionAuthFactor.objects.create(
            session=self.session,
            auth_factor=self.auth_factor,
        )

        self.tokens = OtpBypassToken.generate_tokens()
        self.otp_bypass_tokens = OtpBypassToken.objects.bulk_create(
            [
                OtpBypassToken(user=self.user, token=token)
                for token in self.tokens
            ]
        )

    def test_authenticate(self):
        """Can authenticate by bypassing a user's enabled OTP auth factor."""
        request = self.request_factory.post("/", user=self.user)

        user = self.backend.authenticate(request, token=next(iter(self.tokens)))

        assert user == self.user
        assert self.otp_bypass_tokens[0].id is None
