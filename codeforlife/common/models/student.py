from uuid import uuid4
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .profile import UserProfile
from .school_class import Class


class StudentModelManager(models.Manager):
    def get_random_username(self):
        while True:
            random_username = uuid4().hex[:30]  # generate a random username
            if not User.objects.filter(username=random_username).exists():
                return random_username

    def schoolFactory(self, klass, name, password, login_id=None):
        user = User.objects.create_user(username=self.get_random_username(), password=password, first_name=name)
        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(class_field=klass, user=user_profile, new_user=user, login_id=login_id)

    def independentStudentFactory(self, name, email, password):
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)

        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(user=user_profile, new_user=user)


class Student(models.Model):
    class_field = models.ForeignKey(Class, related_name="students", null=True, blank=True, on_delete=models.CASCADE)
    # hashed uuid used for the unique direct login url
    login_id = models.CharField(max_length=64, null=True)
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    new_user = models.OneToOneField(User, related_name="new_student", null=True, blank=True, on_delete=models.CASCADE)
    pending_class_request = models.ForeignKey(
        Class, related_name="class_request", null=True, blank=True, on_delete=models.SET_NULL
    )
    blocked_time = models.DateTimeField(null=True, blank=True)

    objects = StudentModelManager()

    def is_independent(self):
        return not self.class_field

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"


class JoinReleaseStudent(models.Model):
    """
    To keep track when a student is released to be independent student or
    joins a class to be a school student.
    """

    JOIN = "join"
    RELEASE = "release"

    student = models.ForeignKey(Student, related_name="student", on_delete=models.CASCADE)
    # either "release" or "join"
    action_type = models.CharField(max_length=64)
    action_time = models.DateTimeField(default=timezone.now)
