"""
© Ocado Group
Created on 29/01/2024 at 16:46:24(+00:00).
"""

import string
import typing as t
from itertools import groupby

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.crypto import get_random_string

from .user import User


class OtpBypassToken(models.Model):
    length = 8
    allowed_chars = string.ascii_lowercase
    max_count = 10
    max_count_validation_error = ValidationError(
        f"Exceeded max count of {max_count}"
    )

    class Manager(models.Manager["OtpBypassToken"]):
        def create(self, token: str, **kwargs):  # type: ignore[override]
            return super().create(token=make_password(token), **kwargs)

        def bulk_create(  # type: ignore[override]
            self,
            otp_bypass_tokens: t.List["OtpBypassToken"],
            *args,
            **kwargs,
        ):
            def key(otp_bypass_token: OtpBypassToken):
                return otp_bypass_token.user.id

            otp_bypass_tokens.sort(key=key)
            for user_id, group in groupby(otp_bypass_tokens, key=key):
                if (
                    len(list(group))
                    + OtpBypassToken.objects.filter(user_id=user_id).count()
                    > OtpBypassToken.max_count
                ):
                    raise OtpBypassToken.max_count_validation_error

            for otp_bypass_token in otp_bypass_tokens:
                otp_bypass_token.token = make_password(otp_bypass_token.token)

            return super().bulk_create(otp_bypass_tokens, *args, **kwargs)

    objects: Manager = Manager()

    user = models.ForeignKey(
        User,
        related_name="otp_bypass_tokens",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        max_length=length,
        validators=[MinLengthValidator(length)],
    )

    def save(self, *args, **kwargs):
        if self.id is None:
            if (
                OtpBypassToken.objects.filter(user=self.user).count()
                >= OtpBypassToken.max_count
            ):
                raise OtpBypassToken.max_count_validation_error

        return super().save(*args, **kwargs)

    def check_token(self, token: str):
        if check_password(token.lower(), self.token):
            self.delete()
            return True
        return False

    @classmethod
    def generate_tokens(cls, count: int = max_count):
        """Generates a number of tokens.

        Args:
            count: The number of tokens to generate. Default to max.

        Returns:
            Raw tokens that are random and unique.
        """

        tokens: t.Set[str] = set()
        while len(tokens) < count:
            tokens.add(get_random_string(cls.length, cls.allowed_chars))

        return tokens
