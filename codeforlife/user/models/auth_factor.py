"""
© Ocado Group
Created on 20/02/2024 at 15:41:36(+00:00).
"""

import typing as t

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from ...types import Validators
from ...validators import AsciiNumericCharSetValidator
from .user import User

if t.TYPE_CHECKING:  # pragma: no cover
    from .session_auth_factor import SessionAuthFactor


class AuthFactor(models.Model):
    """A user's enabled authentication factor."""

    sessions: QuerySet["SessionAuthFactor"]

    otp_validators: Validators = [
        AsciiNumericCharSetValidator(),
        MinLengthValidator(6),
        MaxLengthValidator(6),
    ]

    # pylint: disable-next=too-many-ancestors
    class Type(models.TextChoices):
        """The type of authentication factor."""

        OTP = "otp", _("one-time password")

    user = models.ForeignKey(
        User,
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    type = models.TextField(choices=Type.choices)

    class Meta:
        unique_together = ["user", "type"]

    def __str__(self):
        return str(self.type)
