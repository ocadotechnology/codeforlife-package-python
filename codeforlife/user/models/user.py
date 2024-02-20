"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import string
import typing as t

from common.models import UserProfile

# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import User as _User
from django.contrib.auth.models import UserManager
from django.db.models.query import QuerySet
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta
from pyotp import TOTP

from . import auth_factor, otp_bypass_token, session
from .klass import Class
from .student import Independent, Student
from .teacher import (
    AdminSchoolTeacher,
    NonAdminSchoolTeacher,
    NonSchoolTeacher,
    SchoolTeacher,
    Teacher,
)


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

    @property
    def totp(self):
        """Time-based one-time-password for user."""
        return TOTP(self.otp_secret)

    @property
    def totp_provisioning_uri(self):
        """URI provision for the user's time-based one-time-password."""
        return self.totp.provisioning_uri(
            name=self.email,
            issuer_name="Code for Life",
        )


AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class TeacherUserManager(UserManager[AnyUser], t.Generic[AnyUser]):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(new_teacher__isnull=False, new_student__isnull=True)
        )


class TeacherUser(User):
    """A user that is a teacher."""

    teacher: Teacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: TeacherUserManager[  # type: ignore[misc]
        "TeacherUser"
    ] = TeacherUserManager()  # type: ignore[assignment]


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class SchoolTeacherUserManager(TeacherUserManager[AnyUser], t.Generic[AnyUser]):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__school__isnull=False)


class SchoolTeacherUser(User):
    """A user that is a teacher in a school."""

    teacher: SchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: SchoolTeacherUserManager[  # type: ignore[misc]
        "SchoolTeacherUser"
    ] = SchoolTeacherUserManager()  # type: ignore[assignment]


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class AdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["AdminSchoolTeacherUser"]
):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__is_admin=True)


class AdminSchoolTeacherUser(User):
    """A user that is an admin-teacher in a school."""

    teacher: AdminSchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: AdminSchoolTeacherUserManager = (  # type: ignore[misc]
        AdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonAdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["NonAdminSchoolTeacherUser"]
):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__is_admin=False)


class NonAdminSchoolTeacherUser(User):
    """A user that is a non-admin-teacher in a school."""

    teacher: NonAdminSchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonAdminSchoolTeacherUserManager = (  # type: ignore[misc]
        NonAdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonSchoolTeacherUserManager(TeacherUserManager["NonSchoolTeacherUser"]):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__school__isnull=True)


class NonSchoolTeacherUser(User):
    """A user that is a teacher not in a school."""

    teacher: NonSchoolTeacher
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonSchoolTeacherUserManager = (  # type: ignore[misc]
        NonSchoolTeacherUserManager()  # type: ignore[assignment]
    )


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class StudentUserManager(UserManager["StudentUser"]):
    def create_user(  # type: ignore[override]
        self,
        first_name: str,
        klass: Class,
        **extra_fields,
    ):
        """Create a student-user."""
        username = None
        while username is None or self.filter(username=username).exists():
            username = get_random_string(length=30)

        # pylint: disable-next=protected-access
        password = StudentUser._get_random_password()

        user = super().create_user(
            **extra_fields,
            first_name=first_name,
            username=username,
            password=password,
        )

        # pylint: disable-next=protected-access
        user._password = password

        Student.objects.create(
            class_field=klass,
            user=UserProfile.objects.create(user=user),
            new_user=user,
            # pylint: disable-next=protected-access
            login_id=StudentUser._get_random_login_id(),
        )

        return user

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                new_teacher__isnull=True,
                new_student__isnull=False,
                # TODO: remove in new model
                new_student__class_field__isnull=False,
            )
        )


class StudentUser(User):
    """A user that is a student."""

    teacher: None
    student: Student

    class Meta(TypedModelMeta):
        proxy = True

    objects: StudentUserManager = (  # type: ignore[misc]
        StudentUserManager()  # type: ignore[assignment]
    )

    @staticmethod
    def _get_random_password():
        return get_random_string(length=6, allowed_chars=string.ascii_lowercase)

    # TODO: move this is to Student model in new schema.
    @staticmethod
    def _get_random_login_id():
        login_id = None
        while (
            login_id is None
            or Student.objects.filter(login_id=login_id).exists()
        ):
            login_id = get_random_string(length=64)

        return login_id

    # pylint: disable-next=arguments-differ
    def set_password(self):
        super().set_password(self._get_random_password())
        self.student.login_id = self._get_random_login_id()


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class IndependentUserManager(UserManager["IndependentUser"]):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        # TODO: student__isnull=True in new model
        return (
            super()
            .get_queryset()
            .filter(
                new_teacher__isnull=True,
                new_student__isnull=False,
                new_student__class_field__isnull=True,
            )
        )


class IndependentUser(User):
    """A user that is an independent learner."""

    teacher: None
    student: Independent  # TODO: set to None in new model

    class Meta(TypedModelMeta):
        proxy = True

    objects: IndependentUserManager = (  # type: ignore[misc]
        IndependentUserManager()  # type: ignore[assignment]
    )


TypedUser = t.Union[
    TeacherUser,
    SchoolTeacherUser,
    AdminSchoolTeacherUser,
    NonAdminSchoolTeacherUser,
    NonSchoolTeacherUser,
    StudentUser,
    IndependentUser,
]

AnyTypedUser = t.TypeVar("AnyTypedUser", bound=TypedUser)
