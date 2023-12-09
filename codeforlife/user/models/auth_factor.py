"""
© Ocado Group
Created on 05/12/2023 at 17:47:31(+00:00).

Auth factor model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from . import user as _user


class AuthFactor(WarehouseModel):
    """A user's enabled authentication factors."""

    class Type(models.TextChoices):
        """The type of authentication factor."""

        OTP = "otp", _("one-time password")

    user: "_user.User" = models.ForeignKey(  # type: ignore[assignment]
        "user.User",
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    type = models.TextField(
        _("auth factor type"),
        choices=Type.choices,
        help_text=_("The type of authentication factor."),
    )

    class Meta(TypedModelMeta):
        verbose_name = _("auth factor")
        verbose_name_plural = _("auth factors")
        unique_together = ["user", "type"]

    def __str__(self):
        return str(self.type)
