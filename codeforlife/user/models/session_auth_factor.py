"""
© Ocado Group
Created on 05/12/2023 at 17:43:52(+00:00).

Session auth factor model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from . import auth_factor as _auth_factor
from . import session as _session


class SessionAuthFactor(models.Model):
    """
    A pending auth factor for a user's session. If any auth factors are still
    pending, the user is not authenticated.
    """

    session: "_session.Session" = models.ForeignKey(  # type: ignore[assignment]
        "user.Session",
        related_name="session_auth_factors",
        on_delete=models.CASCADE,
    )

    auth_factor: "_auth_factor.AuthFactor" = (
        models.ForeignKey(  # type: ignore[assignment]
            "user.AuthFactor",
            related_name="session_auth_factors",
            on_delete=models.CASCADE,
        )
    )

    class Meta(TypedModelMeta):
        verbose_name = _("session auth factor")
        verbose_name_plural = _("session auth factors")
        unique_together = ["session", "auth_factor"]

    def __str__(self):
        return str(self.auth_factor)
