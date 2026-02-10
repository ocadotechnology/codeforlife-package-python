# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 14/02/2024 at 17:16:44(+00:00).
"""

import typing as t
from uuid import uuid4

from django.db import models

from .klass import Class
from .user import User, UserProfile

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class StudentModelManager(models.Manager):
    def get_random_username(self):
        while True:
            random_username = uuid4().hex[:30]  # generate a random username
            if not User.objects.filter(username=random_username).exists():
                return random_username

    def schoolFactory(self, klass, name, password, login_id=None):
        user = User.objects.create_user(
            username=self.get_random_username(),
            password=password,
            first_name=name,
        )
        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(
            class_field=klass,
            user=user_profile,
            new_user=user,
            login_id=login_id,
        )

    def independentStudentFactory(self, name, email, password):
        user = User.objects.create_user(
            username=email, email=email, password=password, first_name=name
        )

        user_profile = UserProfile.objects.create(user=user)

        return Student.objects.create(user=user_profile, new_user=user)


class Student(models.Model):
    class_field = models.ForeignKey(
        Class,
        related_name="students",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    # hashed uuid used for the unique direct login url
    login_id = models.CharField(max_length=64, null=True)
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    new_user = models.OneToOneField(
        User,
        related_name="new_student",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    pending_class_request = models.ForeignKey(
        Class,
        related_name="class_request",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    blocked_time = models.DateTimeField(null=True, blank=True)

    objects = StudentModelManager()

    def is_independent(self):
        return not self.class_field

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"


# TODO: This model is legacy and should be removed in the new data schema.
class Independent(Student):
    """An independent student."""

    class_field: None

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(StudentModelManager):
        # pylint: disable-next=missing-function-docstring
        def get_queryset(self):
            return super().get_queryset().filter(class_field__isnull=True)

    objects: models.Manager["Independent"] = Manager()
