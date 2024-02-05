"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t

from common.models import UserProfile

# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import User as _User
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from . import auth_factor, otp_bypass_token, session
from .student import Student
from .teacher import NonSchoolTeacher, SchoolTeacher, Teacher


class User(_User):
    _password: t.Optional[str]

    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["auth_factor.AuthFactor"]  # type: ignore[assignment]
    otp_bypass_tokens: QuerySet[  # type: ignore[assignment]
        "otp_bypass_token.OtpBypassToken"
    ]
    session: "session.Session"  # type: ignore[assignment]
    userprofile: UserProfile

    class Meta(TypedModelMeta):
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
    def is_student(self):
        return self.student is not None

    @property
    def is_teacher(self):
        return self.teacher is not None

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


class TeacherUser(User):
    """A user that is a teacher."""

    teacher: Teacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True


class SchoolTeacherUser(User):
    """A user that is a teacher in a school."""

    teacher: SchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True


class NonSchoolTeacherUser(User):
    """A user that is a teacher not in a school."""

    teacher: NonSchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True


class StudentUser(User):
    """A user that is a student."""

    teacher: None
    student: Student

    class Meta(TypedModelMeta):
        proxy = True


# TODO: uncomment this when using new models.
# class IndependentUser(User):
#     teacher: None
#     student: None

#     class Meta(TypedModelMeta):
#         proxy = True
