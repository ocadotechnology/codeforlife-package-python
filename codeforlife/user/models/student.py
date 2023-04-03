from uuid import uuid4

from django.db import models

from .user import User
from .classroom import Class


class StudentModelManager(models.Manager):
    def get_random_username(self):
        while True:
            random_username = uuid4().hex[:30]  # generate a random username
            if not User.objects.filter(username=random_username).exists():
                return random_username

    def schoolFactory(self, klass, name, password, login_id=None):
        user = User.objects.create_user(username=self.get_random_username(), password=password, first_name=name)

        return Student.objects.create(class_field=klass, user=user, login_id=login_id)

    def independentStudentFactory(self, name, email, password):
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)

        return Student.objects.create(user=user)


class Student(models.Model):
    class_field = models.ForeignKey(Class, related_name="students", null=True, blank=True, on_delete=models.CASCADE)
    # hashed uuid used for the unique direct login url
    login_id = models.CharField(max_length=64, null=True)
    user = models.OneToOneField(User, related_name="student", null=True, blank=True, on_delete=models.CASCADE)
    pending_class_request = models.ForeignKey(
        Class, related_name="class_request", null=True, blank=True, on_delete=models.SET_NULL
    )
    blocked_time = models.DateTimeField(null=True, blank=True)

    objects = StudentModelManager()

    def is_independent(self):
        return not self.class_field

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


def stripStudentName(name):
    return re.sub("[ \t]+", " ", name.strip())
