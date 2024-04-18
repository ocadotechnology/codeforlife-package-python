"""
© Ocado Group
Created on 16/04/2024 at 14:29:21(+01:00).
"""

from ...tests import ModelTestCase
from .auth_factor import AuthFactor


# pylint: disable-next=missing-class-docstring
class TestAuthFactor(ModelTestCase[AuthFactor]):
    def test_str(self):
        """String representation is as expected."""
        auth_factor_type = AuthFactor.Type.OTP
        assert str(AuthFactor(type=auth_factor_type)) == str(auth_factor_type)
