"""
© Ocado Group
Created on 05/12/2023 at 17:44:33(+00:00).

OTP bypass token model.
"""

import typing as t
from itertools import groupby

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from ...models import AbstractModel
from . import user


class OtpBypassToken(AbstractModel):
    max_count = 10
    max_count_validation_error = ValidationError(
        f"Exceeded max count of {max_count}"
    )

    class Manager(models.Manager["OtpBypassToken"]):
        def create(self, token: str, **kwargs):
            return super().create(token=make_password(token), **kwargs)

        def bulk_create(
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

    user: "user.User" = models.ForeignKey(
        "user.User",
        related_name="otp_bypass_tokens",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        max_length=8,
        validators=[MinLengthValidator(8)],
    )

    class Meta:
        unique_together = ["user", "token"]

    def save(self, *args, **kwargs):
        if self.id is None:
            if (
                OtpBypassToken.objects.filter(user=self.user).count()
                >= OtpBypassToken.max_count
            ):
                raise OtpBypassToken.max_count_validation_error

        return super().save(*args, **kwargs)

    def check_token(self, token: str):
        if check_password(token, self.token):
            self.delete()
            return True
        return False
