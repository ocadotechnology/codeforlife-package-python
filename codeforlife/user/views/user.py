from rest_framework.viewsets import ModelViewSet

from ..filters import UserFilter
from ..models import User
from ..serializers import UserSerializer


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch"]
    serializer_class = UserSerializer
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = User.objects.all()
        user: User = self.request.user
        if user.teacher is not None:
            queryset = queryset.filter(
                new_teacher__school=user.teacher.school_id,
                # TODO: add school foreign key to student model.
                new_student__class_field__created_by__school=user.teacher.school_id,
            )
        else:
            queryset = queryset.filter(id=user.id)
        return queryset
