from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View

from ..models import User


class IsSchoolMember(BasePermission):
    def has_permission(self, request: Request, view: View):
        user = request.user
        return isinstance(user, User) and (
            (user.is_teacher and user.teacher.school is not None)
            or (
                user.student is not None
                # TODO: should be user.student.school is not None
                and user.student.class_field is not None
            )
        )
