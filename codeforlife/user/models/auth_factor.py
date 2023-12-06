"""
© Ocado Group
Created on 05/12/2023 at 17:47:31(+00:00).

Auth factor model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...models import AbstractModel
from . import user


class AuthFactor(AbstractModel):
    """A user's enabled authentication factors."""

    class Type(models.TextChoices):
        """The type of authentication factor."""

        OTP = "otp", _("one-time password")

    user: "user.User" = models.ForeignKey(
        "user.User",
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    type = models.TextField(
        _("auth factor type"),
        choices=Type.choices,
        help_text=_("The type of authentication factor."),
    )

    class Meta:  # pylint: disable=missing-class-docstring
        unique_together = ["user", "type"]

    def __str__(self):
        return str(self.type)
