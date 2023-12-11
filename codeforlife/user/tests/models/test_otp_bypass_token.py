from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.crypto import get_random_string

from ...models import OtpBypassToken, User


class TestOtpBypassToken(TestCase):
    def setUp(self):
        self.user = User.objects.get(id=2)

    # TODO: test docstrings.
    # TODO: fix unit tests.

    def test_bulk_create(self):
        token = get_random_string(8)
        otp_bypass_tokens = OtpBypassToken.objects.bulk_create(
            [OtpBypassToken(user=self.user, token=token)]
        )

        assert check_password(token, otp_bypass_tokens[0].token)
        with self.assertRaises(ValidationError):
            OtpBypassToken.objects.bulk_create(
                [
                    OtpBypassToken(
                        user=self.user,
                        token=get_random_string(8),
                    )
                    for _ in range(OtpBypassToken.max_count)
                ]
            )

    def test_create(self):
        token = get_random_string(8)
        otp_bypass_token = OtpBypassToken.objects.create(
            user=self.user, token=token
        )

        assert check_password(token, otp_bypass_token.token)

        OtpBypassToken.objects.bulk_create(
            [
                OtpBypassToken(
                    user=self.user,
                    token=get_random_string(8),
                )
                for _ in range(OtpBypassToken.max_count - 1)
            ]
        )

        with self.assertRaises(ValidationError):
            OtpBypassToken.objects.create(
                user=self.user,
                token=get_random_string(8),
            )

    def test_check_token(self):
        token = get_random_string(8)
        otp_bypass_token = OtpBypassToken.objects.create(
            user=self.user, token=token
        )

        assert otp_bypass_token.check_token(token)
        assert otp_bypass_token.id is None
        with self.assertRaises(OtpBypassToken.DoesNotExist):
            OtpBypassToken.objects.get(
                user=otp_bypass_token.user,
                token=otp_bypass_token.token,
            )
