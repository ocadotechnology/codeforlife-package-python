from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..models import Class, User
from ..permissions import IsSchoolMember
from ..serializers import ClassSerializer


class ClassViewSet(ModelViewSet):
    http_method_names = ["get"]
    lookup_field = "access_code"
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user: User = self.request.user
        if user.is_student:
            return Class.objects.filter(students=user.student)
        elif user.teacher.is_admin:
            # TODO: add school field to class object
            return Class.objects.filter(teacher__school=user.teacher.school)
        else:
            return Class.objects.filter(teacher=user.teacher)
