from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .school import School
from .school_class import Class


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    class_field = models.ForeignKey(Class, null=True, on_delete=models.SET_NULL)
    login_type = models.CharField(max_length=100, null=True)  # for student login

    def __str__(self):
        return f"{self.user} login: {self.login_time} type: {self.login_type}"
