"""
© Ocado Group
Created on 18/04/2024 at 17:26:59(+01:00).
"""

from ...tests import ModelSerializerTestCase
from ..models import IndependentUser, StudentUser, TeacherUser, User
from .user import UserSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class TestUserSerializer(ModelSerializerTestCase[User, User]):
    model_serializer_class = UserSerializer

    # test: to representation

    def test_to_representation__teacher(self):
        """Serialize teacher user to representation."""
        user = TeacherUser.objects.first()
        assert user

        self.assert_to_representation(
            user,
            new_data={
                "requesting_to_join_class": None,
                "teacher": {
                    "id": user.teacher.id,
                    "school": user.teacher.school.id,
                    "is_admin": user.teacher.is_admin,
                },
                "student": None,
            },
            # TODO: remove in new schema.
            non_model_fields={"requesting_to_join_class", "teacher", "student"},
        )

    def test_to_representation__student(self):
        """Serialize student user to representation."""
        user = StudentUser.objects.first()
        assert user

        self.assert_to_representation(
            user,
            new_data={
                "requesting_to_join_class": None,
                "teacher": None,
                "student": {
                    "id": user.student.id,
                    "klass": user.student.class_field.access_code,
                    "school": user.student.class_field.teacher.school.id,
                },
            },
            # TODO: remove in new schema.
            non_model_fields={"requesting_to_join_class", "teacher", "student"},
        )

    def test_to_representation__indy(self):
        """Serialize independent user to representation."""
        user = IndependentUser.objects.first()
        assert user

        self.assert_to_representation(
            user,
            new_data={
                "requesting_to_join_class": None,
                "teacher": None,
                "student": None,
            },
            # TODO: remove in new schema.
            non_model_fields={"requesting_to_join_class", "teacher", "student"},
        )
