"""
© Ocado Group
Created on 16/04/2024 at 14:36:42(+01:00).
"""

from ...tests import ModelTestCase
from .auth_factor import AuthFactor
from .session_auth_factor import SessionAuthFactor


# pylint: disable-next=missing-class-docstring
class TestSessionAuthFactor(ModelTestCase[SessionAuthFactor]):
    def test_str(self):
        """String representation is as expected."""
        auth_factor_type = AuthFactor.Type.OTP
        assert str(
            SessionAuthFactor(auth_factor=AuthFactor(type=auth_factor_type))
        ) == str(auth_factor_type)
