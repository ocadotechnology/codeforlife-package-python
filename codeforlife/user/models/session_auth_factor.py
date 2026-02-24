"""
© Ocado Group
Created on 20/02/2024 at 15:36:28(+00:00).
"""

import typing as t

from django.db import models

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta

    from .auth_factor import AuthFactor
    from .session import Session
else:
    TypedModelMeta = object


class SessionAuthFactor(models.Model):
    """A pending authentication factor for a session."""

    session: "Session"
    session = models.ForeignKey(  # type: ignore[assignment]
        "user.Session",
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    auth_factor: "AuthFactor"
    auth_factor = models.ForeignKey(  # type: ignore[assignment]
        "user.AuthFactor",
        related_name="sessions",
        on_delete=models.CASCADE,
    )

    class Meta(TypedModelMeta):
        unique_together = ["session", "auth_factor"]

    def __str__(self):
        return str(self.auth_factor)
