"""
© Ocado Group
Created on 17/01/2025 at 15:55:22(+00:00).
"""

import pyotp
from django.db.models import signals
from django.dispatch import receiver

from ..models import AuthFactor

# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument


@receiver(signals.post_delete, sender=AuthFactor)
def auth_factor__post_delete(sender, instance: AuthFactor, **kwargs):
    # Create new secret to ensure secrets are not recycled.
    if instance.type == AuthFactor.Type.OTP:
        otp_secret = instance.user.userprofile.otp_secret
        # Ensure the randomly generated new secret is different to the previous.
        while otp_secret == instance.user.userprofile.otp_secret:
            instance.user.userprofile.otp_secret = pyotp.random_base32()

        instance.user.userprofile.save(update_fields=["otp_secret"])
