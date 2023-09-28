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

from common.models import UserProfile
from django.contrib.auth.models import User as _User
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from . import auth_factor, backup_token, session


class User(_User):
    auth_factors: QuerySet["auth_factor.AuthFactor"]
    backup_tokens: QuerySet["backup_token.BackupToken"]
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
            return not self.session.session_auth_factors
        except session.Session.DoesNotExist:
            return False
