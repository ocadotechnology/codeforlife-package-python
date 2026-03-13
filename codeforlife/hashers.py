"""
© Ocado Group
Created on 19/01/2026 at 09:55:44(+00:00).
"""

import hashlib
import hmac

from django.conf import settings


def hash_email(email: str):
    """Create a consistent, salted hash of an email address.

    Args:
        email: The email address to hash.

    Returns:
        A hash of the email address salted with the Django secret key.
    """
    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=email.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
