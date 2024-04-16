"""
© Ocado Group
Created on 20/02/2024 at 15:36:28(+00:00).
"""

from django.db import models

from .auth_factor import AuthFactor
from .session import Session


class SessionAuthFactor(models.Model):
    """A pending authentication factor for a session."""

    session = models.ForeignKey(
        Session,
        related_name="auth_factors",
        on_delete=models.CASCADE,
    )

    auth_factor = models.ForeignKey(
        AuthFactor,
        related_name="sessions",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ["session", "auth_factor"]

    def __str__(self):
        return str(self.auth_factor)
