"""
© Ocado Group
Created on 24/01/2024 at 13:12:05(+00:00).
"""

import typing as t

from django.db.models import Q

from ...views import ModelViewSet
from ..filters import UserFilterSet
from ..models import AnyUser, User
from ..serializers import UserSerializer


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class UserViewSet(ModelViewSet[User, User]):
    request_user_class = User
    model_class = User
    http_method_names = ["get"]
    serializer_class = UserSerializer[User]
    filterset_class = UserFilterSet

    # pylint: disable-next=missing-function-docstring
    def get_queryset(
        self,
        user_class: t.Type[AnyUser] = User,  # type: ignore[assignment]
    ):
        # TODO: remove this in new schema and add to get_queryset
        queryset = user_class.objects.filter(is_active=True)

        user = self.request.auth_user
        if user.student:
            if user.student.class_field is None:
                return queryset.filter(pk=user.pk)

            return queryset.filter(
                Q(new_teacher=user.student.class_field.teacher)
                | Q(new_student__class_field=user.student.class_field)
            ).order_by("pk")

        user = self.request.teacher_user
        if user.teacher.school:
            return queryset.filter(
                Q(new_teacher__school=user.teacher.school_id)
                | (
                    Q(
                        # TODO: add school foreign key to student model.
                        new_student__class_field__teacher__school=(
                            user.teacher.school_id
                        ),
                    )
                    if user.teacher.is_admin
                    else Q(new_student__class_field__teacher=user.teacher)
                )
                | (
                    Q(
                        new_student__pending_class_request__teacher__school=(
                            user.teacher.school_id
                        )
                    )
                    if user.teacher.is_admin
                    else Q(
                        new_student__pending_class_request__teacher=user.teacher
                    )
                )
            ).order_by("pk")

        return queryset.filter(pk=user.pk)

    # pylint: disable-next=missing-function-docstring
    def get_bulk_queryset(  # pragma: no cover
        self,
        lookup_values: t.Collection,
        user_class: t.Type[AnyUser] = User,  # type: ignore[assignment]
    ):
        return self.get_queryset(user_class).filter(
            **{f"{self.lookup_field}__in": lookup_values}
        )
