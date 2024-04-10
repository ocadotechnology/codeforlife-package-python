"""
© Ocado Group
Created on 24/01/2024 at 13:47:53(+00:00).
"""

from ...permissions import OR
from ...views import ModelViewSet
from ..models import Class
from ..models import User as RequestUser
from ..permissions import IsStudent, IsTeacher
from ..serializers import ClassSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class ClassViewSet(ModelViewSet[RequestUser, Class]):
    http_method_names = ["get"]
    lookup_field = "access_code"
    serializer_class = ClassSerializer

    def get_permissions(self):
        # Only school-teachers can list classes.
        if self.action == "list":
            return [OR(IsTeacher(is_admin=True), IsTeacher(in_class=True))]

        return [
            OR(
                IsStudent(),
                OR(IsTeacher(is_admin=True), IsTeacher(in_class=True)),
            )
        ]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = self.request.auth_user
        if user.student:
            return Class.objects.filter(students=user.student)

        user = self.request.school_teacher_user
        if user.teacher.is_admin:
            return Class.objects.filter(teacher__school=user.teacher.school)

        return Class.objects.filter(teacher=user.teacher)
