"""
© Ocado Group
Created on 24/01/2024 at 13:38:15(+00:00).
"""

from ...permissions import AllowNone
from ...views import ModelViewSet
from ..models import School
from ..permissions import InSchool
from ..serializers import SchoolSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class SchoolViewSet(ModelViewSet[School]):
    http_method_names = ["get"]
    serializer_class = SchoolSerializer

    def get_permissions(self):
        # No one is allowed to list schools.
        if self.action == "list":
            return [AllowNone()]

        return [InSchool()]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = self.request_user
        if user.student:
            return School.objects.filter(
                # TODO: should be user.student.school_id
                id=user.student.class_field.teacher.school_id
            )

        user = self.request_school_teacher_user
        return School.objects.filter(id=user.teacher.school_id)
