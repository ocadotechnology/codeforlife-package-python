from rest_framework.viewsets import ModelViewSet

from ..filters import UserFilterSet
from ..models import User
from ..serializers import UserSerializer


class UserViewSet(ModelViewSet):
    http_method_names = ["get"]
    serializer_class = UserSerializer
    filterset_class = UserFilterSet

    def get_queryset(self):
        user: User = self.request.user
        if user.teacher is None:
            return User.objects.filter(id=user.id)

        teachers = User.objects.filter(
            new_teacher__school=user.teacher.school_id
        )
        students = User.objects.filter(
            # TODO: add school foreign key to student model.
            new_student__class_field__teacher__school=user.teacher.school_id,
        )

        return teachers | students
