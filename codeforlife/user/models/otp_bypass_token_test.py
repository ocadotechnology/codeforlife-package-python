"""
© Ocado Group
Created on 24/01/2024 at 16:17:22(+00:00).
"""

from django.contrib.auth.hashers import check_password

from ...tests import ModelTestCase
from .otp_bypass_token import OtpBypassToken
from .user import User


# pylint: disable-next=missing-class-docstring
class TestOtpBypassToken(ModelTestCase[OtpBypassToken]):
    fixtures = ["school_2"]

    def setUp(self):
        user = User.objects.filter(otp_bypass_tokens__isnull=False).first()
        assert user
        self.user = user

    def test_objects__bulk_create(self):
        """Can bulk create a new set of tokens."""
        original_otp_bypass_tokens = list(self.user.otp_bypass_tokens.all())

        otp_bypass_tokens = OtpBypassToken.objects.bulk_create(self.user)

        for otp_bypass_token in original_otp_bypass_tokens:
            self.assert_does_not_exist(otp_bypass_token)

        assert len(otp_bypass_tokens) == OtpBypassToken.max_count
        assert len(otp_bypass_tokens) == self.user.otp_bypass_tokens.count()

        for otp_bypass_token in otp_bypass_tokens:
            # pylint: disable-next=protected-access
            raw_token = otp_bypass_token._token
            assert raw_token
            assert len(raw_token) == OtpBypassToken.length
            assert all(
                char in OtpBypassToken.allowed_chars for char in raw_token
            )
            assert check_password(raw_token, otp_bypass_token.token)

    def test_save(self):
        """Cannot create or update a single instance."""
        with self.assert_raises_integrity_error():
            OtpBypassToken().save()

    def test_check_token(self):
        """Can check a single token."""
        otp_bypass_token = self.user.otp_bypass_tokens.first()
        assert otp_bypass_token

        assert not otp_bypass_token.check_token("--------")
        otp_bypass_token.refresh_from_db()  # assert exists

        assert otp_bypass_token.check_token("aaaaaaaa")
        self.assert_does_not_exist(otp_bypass_token)
