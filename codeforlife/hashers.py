"""
© Ocado Group
Created on 19/01/2026 at 09:55:44(+00:00).
"""

import hashlib
import hmac

from django.conf import settings


def hash_credential(credential: str):
    """Create a consistent, salted hash of a credential.

    Args:
        credential: The credential to hash.

    Returns:
        A hash of the credential salted with the Django secret key.
    """
    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=credential.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
