"""
© Ocado Group
Created on 24/01/2024 at 13:12:05(+00:00).
"""

import typing as t

from ...views import ModelViewSet
from ..filters import UserFilterSet
from ..models import User
from ..serializers import UserSerializer


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class UserViewSet(ModelViewSet[User]):
    http_method_names = ["get"]
    serializer_class = UserSerializer
    filterset_class = UserFilterSet

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        user = t.cast(User, self.request.user)
        if user.is_student:
            if user.student.class_field is None:
                return User.objects.filter(id=user.id)

            teachers = User.objects.filter(
                new_teacher=user.student.class_field.teacher
            )
            students = User.objects.filter(
                new_student__class_field=user.student.class_field
            )

            return teachers | students

        teachers = User.objects.filter(
            new_teacher__school=user.teacher.school_id
        )
        students = (
            User.objects.filter(
                # TODO: add school foreign key to student model.
                new_student__class_field__teacher__school=user.teacher.school_id,
            )
            if user.teacher.is_admin
            else User.objects.filter(
                new_student__class_field__teacher=user.teacher
            )
        )

        return teachers | students
