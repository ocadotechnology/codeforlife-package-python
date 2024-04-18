"""
© Ocado Group
Created on 16/04/2024 at 14:40:11(+01:00).
"""

from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from ...tests import ModelTestCase
from .session import Session


# pylint: disable-next=missing-class-docstring
class TestSession(ModelTestCase[Session]):
    def test_is_expired(self):
        """Can check if a session is expired."""
        now = timezone.now()

        session = Session(expire_date=now - timedelta(hours=1))
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            assert session.is_expired
            timezone_now.assert_called_once()

        session = Session(expire_date=now + timedelta(hours=1))
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            assert not session.is_expired
            timezone_now.assert_called_once()
