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
from django_stubs_ext.db.models import TypedModelMeta
from pyotp import TOTP

from .klass import Class
from .student import Independent, Student
from .teacher import (
    AdminSchoolTeacher,
    NonAdminSchoolTeacher,
    NonSchoolTeacher,
    SchoolTeacher,
    Teacher,
    teacher_as_type,
)

if t.TYPE_CHECKING:
    from .auth_factor import AuthFactor
    from .otp_bypass_token import OtpBypassToken
    from .session import Session


class User(_User):
    _password: t.Optional[str]

    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["AuthFactor"]  # type: ignore[assignment]
    otp_bypass_tokens: QuerySet["OtpBypassToken"]  # type: ignore[assignment]
    session: "Session"  # type: ignore[assignment]
    userprofile: UserProfile

    class Meta(TypedModelMeta):
        proxy = True

    @property
    def is_authenticated(self):
        """
        Check if the user has any pending auth factors.
        """
        # pylint: disable-next=import-outside-toplevel
        from .session import Session

        try:
            return not self.session.auth_factors.exists()
        except Session.DoesNotExist:
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

    def as_type(self, typed_user_class: t.Type["AnyTypedUser"]):
        """Convert this generic user to a typed user.

        Args:
            typed_user_class: The type of user to convert to.

        Returns:
            An instance of the typed user.
        """
        return typed_user_class(
            pk=self.pk,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            is_active=self.is_active,
            email=self.email,
            is_staff=self.is_staff,
            date_joined=self.date_joined,
            is_superuser=self.is_superuser,
            password=self.password,
            last_login=self.last_login,
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
            .prefetch_related("new_teacher")
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


class SchoolTeacherUser(TeacherUser):
    """A user that is a teacher in a school."""

    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: SchoolTeacherUserManager[  # type: ignore[misc]
        "SchoolTeacherUser"
    ] = SchoolTeacherUserManager()  # type: ignore[assignment]

    @property
    def teacher(self):
        return teacher_as_type(super().teacher, SchoolTeacher)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class AdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["AdminSchoolTeacherUser"]
):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__is_admin=True)


# pylint: disable-next=too-many-ancestors
class AdminSchoolTeacherUser(SchoolTeacherUser):
    """A user that is an admin-teacher in a school."""

    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: AdminSchoolTeacherUserManager = (  # type: ignore[misc]
        AdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        return teacher_as_type(super().teacher, AdminSchoolTeacher)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonAdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["NonAdminSchoolTeacherUser"]
):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__is_admin=False)


# pylint: disable-next=too-many-ancestors
class NonAdminSchoolTeacherUser(SchoolTeacherUser):
    """A user that is a non-admin-teacher in a school."""

    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonAdminSchoolTeacherUserManager = (  # type: ignore[misc]
        NonAdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        return teacher_as_type(super().teacher, NonAdminSchoolTeacher)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonSchoolTeacherUserManager(TeacherUserManager["NonSchoolTeacherUser"]):
    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return super().get_queryset().filter(new_teacher__school__isnull=True)


class NonSchoolTeacherUser(TeacherUser):
    """A user that is a teacher not in a school."""

    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonSchoolTeacherUserManager = (  # type: ignore[misc]
        NonSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        return teacher_as_type(super().teacher, NonSchoolTeacher)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class StudentUserManager(UserManager["StudentUser"]):
    def create_user(  # type: ignore[override]
        self,
        first_name: str,
        klass: Class,
        **extra_fields,
    ):
        """Create a student-user."""
        # pylint: disable-next=protected-access
        password = StudentUser._get_random_password()

        user = super().create_user(
            **extra_fields,
            first_name=first_name,
            username=StudentUser.get_random_username(),
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
            .prefetch_related("new_student")
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

    @staticmethod
    def get_random_username():
        username = None

        while (
            username is None or User.objects.filter(username=username).exists()
        ):
            username = get_random_string(length=30)

        return username

    # pylint: disable-next=arguments-differ
    def set_password(self, raw_password: t.Optional[str] = None):
        super().set_password(raw_password or self._get_random_password())
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
            .prefetch_related("new_student")
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
