"""
© Ocado Group
Created on 18/04/2024 at 17:26:59(+01:00).
"""

from ...tests import ModelSerializerTestCase
from .user import User


# pylint: disable-next=missing-class-docstring
class TestSchoolTeacherInvitationSerializer(
    ModelSerializerTestCase[User, User]
):
    pass
