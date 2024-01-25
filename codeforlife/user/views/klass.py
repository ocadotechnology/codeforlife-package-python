"""
© Ocado Group
Created on 24/01/2024 at 13:47:53(+00:00).
"""

import typing as t

from ...views import ModelViewSet
from ..models import Class, User
from ..permissions import InSchool
from ..serializers import ClassSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class ClassViewSet(ModelViewSet[Class]):
    http_method_names = ["get"]
    lookup_field = "access_code"
    serializer_class = ClassSerializer
    permission_classes = [InSchool]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = t.cast(User, self.request.user)
        if user.is_student:
            return Class.objects.filter(students=user.student)
        if user.teacher.is_admin:
            # TODO: add school field to class object
            return Class.objects.filter(teacher__school=user.teacher.school)

        return Class.objects.filter(teacher=user.teacher)
