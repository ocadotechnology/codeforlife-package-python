"""
© Ocado Group
Created on 05/02/2024 at 16:33:52(+00:00).
"""

import typing as t

from django.contrib.auth.models import AnonymousUser
from rest_framework.views import APIView as _APIView

from ..user.models import (
    AdminSchoolTeacherUser,
    IndependentUser,
    NonAdminSchoolTeacherUser,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    StudentUser,
    TeacherUser,
    User,
)


# pylint: disable-next=missing-class-docstring
class APIView(_APIView):
    @property
    def request_user(self):
        """
        The user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(User, self.request.user)

    @property
    def request_teacher_user(self):
        """
        The teacher-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(TeacherUser, self.request.user)

    @property
    def request_school_teacher_user(self):
        """
        The school-teacher-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(SchoolTeacherUser, self.request.user)

    @property
    def request_admin_school_teacher_user(self):
        """
        The admin-school-teacher-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(AdminSchoolTeacherUser, self.request.user)

    @property
    def request_non_admin_school_teacher_user(self):
        """
        The non-admin-school-teacher-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(NonAdminSchoolTeacherUser, self.request.user)

    @property
    def request_non_school_teacher_user(self):
        """
        The non-school-teacher-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(NonSchoolTeacherUser, self.request.user)

    @property
    def request_student_user(self):
        """
        The student-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(StudentUser, self.request.user)

    @property
    def request_indy_user(self):
        """
        The independent-user that made the request.
        Assumes the user has authenticated.
        """

        return t.cast(IndependentUser, self.request.user)

    @property
    def request_anon_user(self):
        """
        The user that made the request.
        Assumes the user has not authenticated.
        """

        return t.cast(AnonymousUser, self.request.user)
