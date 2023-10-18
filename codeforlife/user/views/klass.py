from rest_framework.viewsets import ModelViewSet

from ..models import Class, User
from ..serializers import ClassSerializer


class ClassViewSet(ModelViewSet):
    lookup_field = "access_code"
    serializer_class = ClassSerializer

    def get_queryset(self):
        user: User = self.request.user
        if user.teacher is None:
            return Class.objects.filter(students=user)
        elif user.teacher.is_admin:
            # TODO: add school field to class object
            return Class.objects.filter(teacher__school=user.teacher.school)
        else:
            return Class.objects.filter(teacher=user)
