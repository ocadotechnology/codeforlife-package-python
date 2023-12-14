"""
© Ocado Group
Created on 14/12/2023 at 14:06:05(+00:00).
"""

from rest_framework.viewsets import ModelViewSet

from ..filters import UserFilterSet
from ..models import User
from ..serializers import UserSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class UserViewSet(ModelViewSet):
    http_method_names = ["get"]
    serializer_class = UserSerializer
    filterset_class = UserFilterSet

    def get_queryset(self):
        user = self.request.user
        if not isinstance(user, User):
            return User.objects.none()

        if user.student:
            return User.objects.filter(student__klass_id=user.student.klass_id)

        if user.teacher:
            teachers = User.objects.none()
            students = User.objects.none()

            if user.teacher.school_id:
                teachers = User.objects.filter(
                    teacher__school_id=user.teacher.school_id
                )

                students = (
                    User.objects.filter(
                        student__school_id=user.teacher.school_id
                    )
                    if user.teacher.is_admin
                    else User.objects.filter(
                        student__klass__teacher=user.teacher
                    )
                )

            return teachers | students

        return User.objects.filter(id=user.id)
