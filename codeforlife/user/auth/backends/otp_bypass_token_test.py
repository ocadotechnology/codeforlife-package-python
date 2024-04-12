"""
© Ocado Group
Created on 10/04/2024 at 13:17:18(+01:00).
"""

from ....tests import APIRequestFactory, TestCase
from ...models import AuthFactor, User
from .otp_bypass_token import OtpBypassTokenBackend


# pylint: disable-next=missing-class-docstring,too-many-instance-attributes
class TestTokenBackend(TestCase):
    fixtures = ["school_2", "school_2_sessions"]

    def setUp(self):
        self.backend = OtpBypassTokenBackend()
        self.request_factory = APIRequestFactory(User)

        user = User.objects.filter(
            otp_bypass_tokens__isnull=False,
            session__isnull=False,
            session__auth_factors__auth_factor__type__in=[AuthFactor.Type.OTP],
        ).first()
        assert user
        self.user = user

    def test_authenticate(self):
        """Can authenticate by bypassing a user's enabled OTP auth factor."""
        otp_bypass_token_count = self.user.otp_bypass_tokens.count()

        user = self.backend.authenticate(
            request=self.request_factory.post("/", user=self.user),
            token="aaaaaaaa",
        )

        assert user == self.user
        assert user.otp_bypass_tokens.count() == otp_bypass_token_count - 1
