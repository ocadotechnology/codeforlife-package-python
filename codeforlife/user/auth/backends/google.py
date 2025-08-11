"""
© Ocado Group
Created on 01/07/2025 at 12:48:13(+01:00).
"""

import typing as t

import requests
from django.conf import settings

from ....request import HttpRequest
from ....types import JsonDict
from ...cache import GoogleAccessToken
from ...models import ContactableUser, UserProfile
from .base import BaseBackend


class GoogleBackend(BaseBackend):
    """Authenticate a user using the code returned by Google's callback URL."""

    user_class = ContactableUser

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        code: t.Optional[str] = None,
        code_verifier: t.Optional[str] = None,
        redirect_uri: t.Optional[str] = None,
        **kwargs,
    ):
        if code is None or code_verifier is None or redirect_uri is None:
            return None

        # Get user's google-access-token.
        response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
            },
            timeout=5,
        )
        if not response.ok:
            return None

        token_data: JsonDict = response.json()
        if "error" in token_data:
            return None
        access_token = t.cast(str, token_data["access_token"])
        access_token_expires_in = t.cast(int, token_data["expires_in"])

        response = requests.get(
            url="https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if not response.ok:
            return None

        user_data: JsonDict = response.json()
        email = t.cast(str, user_data["email"])

        user, user_was_created = ContactableUser.objects.get_or_create(
            email=email.lower(),
            defaults={
                "first_name": user_data["given_name"],
                "last_name": user_data["family_name"],
            },
        )

        if user_was_created:
            UserProfile.objects.create(
                user=user,
                is_verified=user_data["email_verified"],
            )

        GoogleAccessToken.set(
            key=user.id,
            value=access_token,
            timeout=access_token_expires_in,
        )

        return user
