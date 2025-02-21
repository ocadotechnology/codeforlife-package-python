"""
© Ocado Group
Created on 24/01/2024 at 16:17:22(+00:00).
"""

from cryptography.fernet import Fernet
from django.conf import settings

from ...tests import ModelTestCase
from .otp_bypass_token import OtpBypassToken
from .user import User


# pylint: disable-next=missing-class-docstring
class TestOtpBypassToken(ModelTestCase[OtpBypassToken]):
    fixtures = ["school_2"]

    def setUp(self):
        self.fernet = Fernet(settings.SECRET_KEY)

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
            decrypted_token = otp_bypass_token.decrypted_token
            assert len(decrypted_token) == OtpBypassToken.length
            assert all(
                char in OtpBypassToken.allowed_chars for char in decrypted_token
            )

    def test_save(self):
        """Cannot create or update a single instance."""
        with self.assert_raises_integrity_error():
            OtpBypassToken().save()

    def test_decrypted_token(self):
        """Can get decrypted token as property."""
        token = "test-decrypt"
        otp_bypass_token = OtpBypassToken(
            user=self.user,
            token=self.fernet.encrypt(token.encode()).decode(),
        )
        assert otp_bypass_token.decrypted_token == token

    def test_check_token(self):
        """Can check a single token."""
        otp_bypass_token = self.user.otp_bypass_tokens.first()
        assert otp_bypass_token

        assert not otp_bypass_token.check_token("--------")
        otp_bypass_token.refresh_from_db()  # assert exists

        assert otp_bypass_token.check_token("aaaaaaaa")
        self.assert_does_not_exist(otp_bypass_token)
