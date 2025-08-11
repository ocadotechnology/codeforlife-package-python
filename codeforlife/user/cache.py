"""
© Ocado Group
Created on 11/08/2025 at 11:07:45(+01:00).
"""

from ..cache import BaseCacheDynamicKeyValue

# pylint: disable=signature-differs


class GoogleAccessToken(BaseCacheDynamicKeyValue[int, str]):
    """A user's Google-access-token. The key is the user's ID."""

    @staticmethod
    def make_key(key):
        return f"{key}.google.access_token"

    @classmethod
    def get(cls, key, default=None, version=None):
        google_access_token = super().get(key, default, version)
        if not google_access_token:
            # TODO
            raise NotImplementedError()

        return google_access_token
