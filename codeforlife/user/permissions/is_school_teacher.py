from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View

from ..models import User


class IsSchoolTeacher(BasePermission):
    def has_permission(self, request: Request, view: View):
        user = request.user
        return (
            isinstance(user, User)
            and user.teacher is not None
            and user.teacher.school is not None
        )
