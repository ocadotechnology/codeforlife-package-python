"""
© Ocado Group
Created on 11/08/2025 at 11:07:45(+01:00).
"""

import typing as t

import requests
from django.conf import settings

from ..cache import BaseCacheDynamicKeyValue
from ..types import JsonDict
from .models import GoogleUser


class GoogleAccessToken(BaseCacheDynamicKeyValue[int, str]):
    """A user's Google-access-token. The key is the user's ID."""

    @staticmethod
    def make_key(key):
        return f"{key}.google.access_token"

    @classmethod
    def get(cls, key, default=None, version=None):
        value = super().get(key, default, version)
        if not value:
            user_queryset = GoogleUser.objects.filter(id=key)
            if user_queryset.exists():
                user = user_queryset.get()

                response = requests.post(
                    url="https://oauth2.googleapis.com/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": user.userprofile.google_refresh_token,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    },
                    timeout=10,
                )
                if response.ok:
                    token_data: JsonDict = response.json()
                    access_token = t.cast(str, token_data["access_token"])
                    expires_in = t.cast(int, token_data["expires_in"])
                    token_type = t.cast(str, token_data["token_type"])

                    value = f"{token_type} {access_token}"

                    # -3 seconds to reduce likeliness of using an expired token.
                    cls.set(key=key, value=value, timeout=expires_in - 3)

        return value
