"""
© Ocado Group
Created on 24/01/2024 at 13:38:15(+00:00).
"""

import typing as t

from rest_framework.permissions import IsAuthenticated

from ...views import ModelViewSet
from ..models import School, User
from ..permissions import IsSchoolMember
from ..serializers import SchoolSerializer


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class SchoolViewSet(ModelViewSet[School]):
    http_method_names = ["get"]
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = t.cast(User, self.request.user)
        if user.is_student:
            return School.objects.filter(
                # TODO: should be user.student.school_id
                id=user.student.class_field.teacher.school_id
            )

        return School.objects.filter(id=user.teacher.school_id)
