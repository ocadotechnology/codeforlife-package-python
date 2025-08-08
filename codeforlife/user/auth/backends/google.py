"""
© Ocado Group
Created on 01/07/2025 at 12:48:13(+01:00).
"""

import typing as t

import requests
from django.conf import settings
from django.urls import reverse

from ....request import HttpRequest
from ....types import JsonDict
from ...models import ContactableUser
from .base import BaseBackend


class GoogleBackend(BaseBackend):
    """Authenticate a user using the code returned by Google's callback URL."""

    user_class = ContactableUser

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        code: t.Optional[str] = None,
        code_verifier: t.Optional[str] = None,
        **kwargs,
    ):
        if code is None or code_verifier is None:
            return None

        # Get user access Token
        response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "code_verifier": code_verifier,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": reverse("save-google-token"),
                "grant_type": "authorization_code",
            },
            # headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
        )
        if not response.ok:
            return None

        access_token: JsonDict = response.json()
        if "error" in access_token:
            return None

        # return self.user_class.sync_with_github(
        #     auth=f"{access_token['token_type']} {access_token['access_token']}"
        # )

        return None
