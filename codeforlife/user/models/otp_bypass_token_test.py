"""
© Ocado Group
Created on 24/01/2024 at 16:17:22(+00:00).
"""

from unittest.mock import call, patch

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import OtpBypassToken, User, otp_bypass_token


class TestOtpBypassToken(TestCase):
    def setUp(self):
        self.user = User.objects.get(id=2)

    def test_bulk_create(self):
        token = next(iter(OtpBypassToken.generate_tokens(1)))
        otp_bypass_tokens = OtpBypassToken.objects.bulk_create(
            [OtpBypassToken(user=self.user, token=token)]
        )

        assert check_password(token, otp_bypass_tokens[0].token)
        with self.assertRaises(ValidationError):
            OtpBypassToken.objects.bulk_create(
                [
                    OtpBypassToken(user=self.user, token=token)
                    for token in OtpBypassToken.generate_tokens()
                ]
            )

    def test_create(self):
        token = next(iter(OtpBypassToken.generate_tokens(1)))
        otp_bypass_token = OtpBypassToken.objects.create(
            user=self.user, token=token
        )

        assert check_password(token, otp_bypass_token.token)

        OtpBypassToken.objects.bulk_create(
            [
                OtpBypassToken(user=self.user, token=token)
                for token in OtpBypassToken.generate_tokens(
                    OtpBypassToken.max_count - 1
                )
            ]
        )

        with self.assertRaises(ValidationError):
            OtpBypassToken.objects.create(
                user=self.user,
                token=next(iter(OtpBypassToken.generate_tokens(1))),
            )

    def test_check_token(self):
        token = next(iter(OtpBypassToken.generate_tokens(1)))
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

    def test_generate_tokens(self):
        """
        Generates a number of unique tokens.
        """

        count = 3
        get_random_string_side_effect = [
            "aaaaaaaa",
            "aaaaaaaa",
            "bbbbbbbb",
            "cccccccc",
        ]

        with patch.object(
            otp_bypass_token,
            "get_random_string",
            side_effect=get_random_string_side_effect,
        ) as get_random_string:
            tokens = OtpBypassToken.generate_tokens(count)
            assert len(tokens) == count
            assert tokens == {
                "aaaaaaaa",
                "bbbbbbbb",
                "cccccccc",
            }

            get_random_string.assert_has_calls(
                [
                    call(OtpBypassToken.length, OtpBypassToken.allowed_chars)
                    for _ in range(len(get_random_string_side_effect))
                ]
            )
