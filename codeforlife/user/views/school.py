"""
© Ocado Group
Created on 24/01/2024 at 13:38:15(+00:00).
"""

from ...permissions import OR, AllowNone
from ...views import ModelViewSet
from ..models import School, User
from ..permissions import IsIndependent, IsStudent, IsTeacher
from ..serializers import SchoolSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class SchoolViewSet(ModelViewSet[User, School]):
    request_user_class = User
    model_class = School
    http_method_names = ["get"]
    serializer_class = SchoolSerializer

    # pylint: disable-next=missing-function-docstring
    def get_permissions(self):
        # No one is allowed to list schools.
        if self.action == "list":
            return [AllowNone()]

        return [
            OR(
                OR(IsStudent(), IsTeacher(in_school=True)),
                IsIndependent(is_requesting_to_join_class=True),
            )
        ]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = self.request.auth_user
        if user.student:
            if user.student.pending_class_request:
                return School.objects.filter(
                    # TODO: should be user.requesting_to_join_class.school_id
                    id=user.student.pending_class_request.teacher.school_id
                )
            return School.objects.filter(
                # TODO: should be user.student.school_id
                id=user.student.class_field.teacher.school_id
            )

        user = self.request.school_teacher_user
        return School.objects.filter(id=user.teacher.school_id)
