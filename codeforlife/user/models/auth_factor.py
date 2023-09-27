from django.db import models
from django.utils.translation import gettext_lazy as _

from . import user


class AuthFactor(models.Model):
    class Type(models.TextChoices):
        OTP = "otp", _("one-time password")

    user: "user.User" = models.ForeignKey(
        "user.User",
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    type = models.TextField(choices=Type.choices)

    class Meta:
        unique_together = ["user", "type"]

    def __str__(self):
        return self.type
