from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from .profile import UserProfile
from .school import School


class TeacherModelManager(models.Manager):
    def factory(self, first_name, last_name, email, password):
        user = User.objects.create_user(
            username=email, email=email, password=password, first_name=first_name, last_name=last_name
        )

        user_profile = UserProfile.objects.create(user=user)

        return Teacher.objects.create(user=user_profile, new_user=user)

    # Filter out non active teachers by default
    def get_queryset(self):
        return super().get_queryset().filter(new_user__is_active=True)


class Teacher(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    new_user = models.OneToOneField(User, related_name="new_teacher", null=True, blank=True, on_delete=models.CASCADE)
    school = models.ForeignKey(School, related_name="teacher_school", null=True, blank=True, on_delete=models.SET_NULL)
    is_admin = models.BooleanField(default=False)
    blocked_time = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        "self", related_name="invited_teachers", null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = TeacherModelManager()

    def teaches(self, userprofile):
        if hasattr(userprofile, "student"):
            student = userprofile.student
            return not student.is_independent() and student.class_field.teacher == self

    def has_school(self):
        return self.school is not (None or "")

    def has_class(self):
        return self.class_teacher.exists()

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"
