"""
© Ocado Group
Created on 24/01/2024 at 13:38:15(+00:00).
"""

from ...permissions import OR, AllowNone
from ...views import ModelViewSet
from ..models import School
from ..models import User as RequestUser
from ..permissions import IsStudent, IsTeacher
from ..serializers import SchoolSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class SchoolViewSet(ModelViewSet[RequestUser, School]):
    http_method_names = ["get"]
    serializer_class = SchoolSerializer

    def get_permissions(self):
        # No one is allowed to list schools.
        if self.action == "list":
            return [AllowNone()]

        return [OR(IsStudent(), IsTeacher(in_school=True))]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = self.request.auth_user
        if user.student:
            return School.objects.filter(
                # TODO: should be user.student.school_id
                id=user.student.class_field.teacher.school_id
            )

        user = self.request.school_teacher_user
        return School.objects.filter(id=user.teacher.school_id)
