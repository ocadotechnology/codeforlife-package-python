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
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from . import user as _user


class OtpBypassToken(WarehouseModel):
    """
    A one-time-use token that a user can use to bypass their OTP auth factor.
    Each user has a limited number of OTP-bypass tokens.
    """

    max_count = 10
    max_count_validation_error = ValidationError(
        f"Exceeded max count of {max_count}"
    )

    # pylint: disable-next=missing-class-docstring
    class Manager(models.Manager["OtpBypassToken"]):
        def create(self, token: str, **kwargs):  # type: ignore[override]
            """Create an OTP-bypass token.

            Args:
                token: The token value to be hashed.

            Returns:
                A OtpBypassToken instance.
            """

            return super().create(token=make_password(token), **kwargs)

        def bulk_create(  # type: ignore[override]
            self,
            otp_bypass_tokens: t.List["OtpBypassToken"],
            *args,
            **kwargs,
        ):
            """Bulk create OTP-bypass tokens.

            Args:
                otp_bypass_tokens: The token values to be hashed.

            Returns:
                Many OtpBypassToken instances.
            """

            def key(otp_bypass_token: OtpBypassToken):
                return otp_bypass_token.user.id

            otp_bypass_tokens.sort(key=key)
            for user_id, group in groupby(otp_bypass_tokens, key=key):
                if (
                    len(list(group))
                    + OtpBypassToken.objects.filter(
                        user_id=user_id,
                        delete_after__isnull=True,
                    ).count()
                    > OtpBypassToken.max_count
                ):
                    raise OtpBypassToken.max_count_validation_error

            for otp_bypass_token in otp_bypass_tokens:
                otp_bypass_token.token = make_password(otp_bypass_token.token)

            return super().bulk_create(otp_bypass_tokens, *args, **kwargs)

    objects: Manager = Manager.from_queryset(  # type: ignore[misc]
        WarehouseModel.QuerySet
    )()  # type: ignore[assignment]

    user: "_user.User" = models.ForeignKey(  # type: ignore[assignment]
        "user.User",
        related_name="otp_bypass_tokens",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        max_length=8,
        validators=[MinLengthValidator(8)],
    )

    class Meta(TypedModelMeta):
        verbose_name = _("OTP bypass token")
        verbose_name_plural = _("OTP bypass tokens")
        unique_together = ["user", "token"]

    def save(self, *args, **kwargs):
        if self.id is None:
            if (
                OtpBypassToken.objects.filter(
                    user=self.user,
                    delete_after__isnull=True,
                ).count()
                >= OtpBypassToken.max_count
            ):
                raise OtpBypassToken.max_count_validation_error

        return super().save(*args, **kwargs)

    def check_token(self, token: str):
        """Check if the token matches.

        Args:
            token: Token to check.

        Returns:
            A boolean designating if the token is matches.
        """

        if not self.delete_after and check_password(token, self.token):
            self.delete()
            return True
        return False
