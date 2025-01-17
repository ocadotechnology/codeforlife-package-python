"""
© Ocado Group
Created on 17/01/2025 at 16:04:46(+00:00).
"""

from django.test import TestCase

from ..models import AuthFactor


# pylint: disable-next=missing-class-docstring
class TestAuthFactor(TestCase):
    fixtures = ["school_2"]

    def test_post_delete(self):
        """Deleting an otp-auth-factor assigns a new otp-secret to its user."""
        auth_factor = AuthFactor.objects.filter(
            type=AuthFactor.Type.OTP
        ).first()
        assert auth_factor

        userprofile = auth_factor.user.userprofile
        otp_secret = userprofile.otp_secret

        auth_factor.delete()

        userprofile.refresh_from_db()
        assert otp_secret != userprofile.otp_secret
