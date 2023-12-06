"""
© Ocado Group
Created on 05/12/2023 at 17:43:52(+00:00).

Session auth factor model.
"""

from django.db import models

from . import auth_factor, session


class SessionAuthFactor(models.Model):
    session: "session.Session" = models.ForeignKey(
        "user.Session",
        related_name="session_auth_factors",
        on_delete=models.CASCADE,
    )

    auth_factor: "auth_factor.AuthFactor" = models.ForeignKey(
        "user.AuthFactor",
        related_name="session_auth_factors",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ["session", "auth_factor"]

    def __str__(self):
        return str(self.auth_factor)
