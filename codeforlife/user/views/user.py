"""
© Ocado Group
Created on 24/01/2024 at 13:12:05(+00:00).
"""

import typing as t

from ...views import ModelViewSet
from ..filters import UserFilterSet
from ..models import AnyUser, User
from ..serializers import BaseUserSerializer, UserSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class UserViewSet(ModelViewSet[User]):
    http_method_names = ["get"]
    serializer_class: t.Type[BaseUserSerializer] = UserSerializer
    filterset_class = UserFilterSet

    def get_queryset(
        self,
        user_class: t.Type[AnyUser] = User,  # type: ignore[assignment]
    ):
        user = self.request.auth_user
        if user.student:
            if user.student.class_field is None:
                return user_class.objects.filter(id=user.id)

            teachers = user_class.objects.filter(
                new_teacher=user.student.class_field.teacher
            )
            students = user_class.objects.filter(
                new_student__class_field=user.student.class_field
            )

            return teachers | students

        user = self.request.teacher_user
        if user.teacher.school:
            teachers = user_class.objects.filter(
                new_teacher__school=user.teacher.school_id
            )
            students = (
                user_class.objects.filter(
                    # TODO: add school foreign key to student model.
                    new_student__class_field__teacher__school=user.teacher.school_id,
                )
                if user.teacher.is_admin
                else user_class.objects.filter(
                    new_student__class_field__teacher=user.teacher
                )
            )

            return teachers | students

        return user_class.objects.filter(pk=user.pk)

    def get_bulk_queryset(
        self,
        lookup_values: t.Collection,
        user_class: t.Type[AnyUser] = User,  # type: ignore[assignment]
    ):
        return self.get_queryset(user_class).filter(
            **{f"{self.lookup_field}__in": lookup_values}
        )
