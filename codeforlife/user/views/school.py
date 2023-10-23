from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..models import School, User
from ..permissions import IsSchoolMember
from ..serializers import SchoolSerializer


class SchoolViewSet(ModelViewSet):
    http_method_names = ["get"]
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user: User = self.request.user
        if user.teacher is None:
            return School.objects.filter(
                # TODO: should be user.student.school_id
                id=user.student.class_field.teacher.school_id
            )
        else:
            return School.objects.filter(id=user.teacher.school_id)
