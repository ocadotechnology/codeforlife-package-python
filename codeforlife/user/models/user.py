# from datetime import timedelta
# from enum import Enum

# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import UserManager as AbstractUserManager
# from django.db import models
# from django.utils import timezone


# class UserManager(AbstractUserManager):
#     def create_user(self, username, email=None, password=None, **extra_fields):
#         return super().create_user(username, email, password, **extra_fields)

#     def create_superuser(
#         self, username, email=None, password=None, **extra_fields
#     ):
#         return super().create_superuser(
#             username, email, password, **extra_fields
#         )


# class User(AbstractUser):
#     class Type(str, Enum):
#         TEACHER = "teacher"
#         DEP_STUDENT = "dependent-student"
#         INDEP_STUDENT = "independent-student"

#     developer = models.BooleanField(default=False)
#     is_verified = models.BooleanField(default=False)

#     objects: UserManager = UserManager()

#     def __str__(self):
#         return self.get_full_name()

#     @property
#     def joined_recently(self):
#         return timezone.now() - timedelta(days=7) <= self.date_joined

import typing as t

from common.models import UserProfile
from django.contrib.auth.models import User as _User
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from . import auth_factor, otp_bypass_token, session
from .student import Student
from .teacher import Teacher


class User(_User):
    id: int
    auth_factors: QuerySet["auth_factor.AuthFactor"]
    otp_bypass_tokens: QuerySet["otp_bypass_token.OtpBypassToken"]
    session: "session.Session"
    userprofile: UserProfile

    class Meta:
        proxy = True

    @property
    def is_authenticated(self):
        """
        Check if the user has any pending auth factors.
        """

        try:
            return not self.session.session_auth_factors.exists()
        except session.Session.DoesNotExist:
            return False

    @property
    def student(self) -> t.Optional[Student]:
        try:
            return self.new_student
        except Student.DoesNotExist:
            return None

    @property
    def teacher(self) -> t.Optional[Teacher]:
        try:
            return self.new_teacher
        except Teacher.DoesNotExist:
            return None

    @property
    def otp_secret(self):
        return self.userprofile.otp_secret

    @property
    def last_otp_for_time(self):
        return self.userprofile.last_otp_for_time

    @property
    def is_verified(self):
        return self.userprofile.is_verified

    @property
    def aimmo_badges(self):
        return self.userprofile.aimmo_badges
