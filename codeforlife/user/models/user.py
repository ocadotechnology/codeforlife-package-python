# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""
import string
import typing as t
from datetime import datetime

from common.models import TotalActivity, UserProfile

# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import User as _User
from django.contrib.auth.models import UserManager as _UserManager
from django.db.models import F
from django.db.models.query import QuerySet
from django.utils.crypto import get_random_string
from pyotp import TOTP

from ... import mail
from ...models import AbstractBaseUser
from ...types import Validators
from ...validators import UnicodeAlphanumericCharSetValidator
from .klass import Class
from .school import School

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta

    from .auth_factor import AuthFactor
    from .otp_bypass_token import OtpBypassToken
    from .session import Session
    from .student import Independent, Student
    from .teacher import Teacher
else:
    TypedModelMeta = object


# TODO: add to model validators in new schema.
user_first_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-'",
    )
]
user_last_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-'",
    )
]


# TODO: remove in new schema
class _AbstractBaseUser(AbstractBaseUser):
    password: str = None  # type: ignore[assignment]
    last_login: datetime = None  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        abstract = True


# pylint: disable-next=too-many-ancestors
class User(_AbstractBaseUser, _User):
    """A proxy to Django's user class."""

    _password: t.Optional[str]

    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["AuthFactor"]  # type: ignore[assignment]
    otp_bypass_tokens: QuerySet["OtpBypassToken"]  # type: ignore[assignment]
    session: "Session"  # type: ignore[assignment]
    userprofile: UserProfile

    credential_fields = frozenset(["email", "password"])

    class Meta(TypedModelMeta):
        proxy = True

    @property
    def is_authenticated(self):
        return (
            not self.session.auth_factors.exists()
            and self.userprofile.is_verified
            if super().is_authenticated
            else False
        )

    @property
    def student(self) -> t.Optional["Student"]:
        """A user's student-profile."""
        # pylint: disable-next=import-outside-toplevel
        from .student import Student

        try:
            # pylint: disable-next=no-member
            return self.new_student  # type: ignore[attr-defined]
        except Student.DoesNotExist:
            return None

    @property
    def teacher(self) -> t.Optional["Teacher"]:
        """A user's teacher-profile."""
        # pylint: disable-next=import-outside-toplevel
        from .teacher import Teacher

        try:
            # pylint: disable-next=no-member
            return self.new_teacher  # type: ignore[attr-defined]
        except Teacher.DoesNotExist:
            return None

    @property
    def otp_secret(self):
        """Shorthand for user-profile field."""
        return self.userprofile.otp_secret

    @property
    def last_otp_for_time(self):
        """Shorthand for user-profile field."""
        return self.userprofile.last_otp_for_time

    @property
    def is_verified(self):
        """Shorthand for user-profile field."""
        return self.userprofile.is_verified

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

    def as_type(self, user_class: t.Type["AnyUser"]):
        """Convert this generic user to a typed user.

        Args:
            user_class: The type of user to convert to.

        Returns:
            An instance of the typed user.
        """
        return user_class(
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

    def anonymize(self):
        """Anonymize the user."""
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.is_active = False
        self.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
                "username",
                "is_active",
            ]
        )


AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring
class UserManager(_UserManager[AnyUser], t.Generic[AnyUser]):
    def filter_users(self, queryset: QuerySet[User]):
        """Filter the users to the specific type.

        Args:
            queryset: The queryset of users to filter.

        Returns:
            A subset of the queryset of users.
        """
        return queryset

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return self.filter_users(super().get_queryset().filter(is_active=True))


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class ContactableUserManager(UserManager[AnyUser], t.Generic[AnyUser]):
    def filter_users(self, queryset: QuerySet[User]):
        return queryset.exclude(email__isnull=True).exclude(email="")


# pylint: disable-next=too-many-ancestors
class ContactableUser(User):
    """A user that can be contacted."""

    class Meta(TypedModelMeta):
        proxy = True

    def add_contact_to_dot_digital(self):
        """Add contact info to DotDigital."""
        mail.add_contact(self.email)

    def remove_contact_from_dot_digital(self):
        """Remove contact info from DotDigital."""
        mail.remove_contact(self.email)

    # pylint: disable-next=arguments-differ
    def email_user(  # type: ignore[override]
        self,
        campaign_id: int,
        personalization_values: t.Optional[t.Dict[str, str]] = None,
        **kwargs,
    ):
        kwargs["to_addresses"] = [self.email]
        mail.send_mail(
            campaign_id=campaign_id,
            personalization_values=personalization_values,
            **kwargs,
        )


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class TeacherUserManager(ContactableUserManager[AnyUser], t.Generic[AnyUser]):
    # pylint: disable-next=too-many-arguments
    def create_user(  # type: ignore[override]
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        school: t.Optional[School] = None,
        is_admin: bool = False,
        is_verified: bool = False,
        **extra_fields,
    ):
        """Create a teacher-user."""
        # pylint: disable-next=import-outside-toplevel
        from .teacher import Teacher

        assert "username" not in extra_fields

        user = super().create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )

        Teacher.objects.create(
            school=school,
            new_user=user,
            user=UserProfile.objects.create(user=user, is_verified=is_verified),
            is_admin=is_admin,
        )

        # TODO: delete this in new data schema
        TotalActivity.objects.update(
            teacher_registrations=F("teacher_registrations") + 1
        )

        return user

    def filter_users(self, queryset: QuerySet[User]):
        return (
            super()
            .filter_users(queryset)
            .filter(new_teacher__isnull=False, new_student__isnull=True)
        )

    def get_queryset(self):
        return super().get_queryset().prefetch_related("new_teacher")


# pylint: disable-next=too-many-ancestors
class TeacherUser(ContactableUser):
    """A user that is a teacher."""

    teacher: "Teacher"
    student: None

    class Meta(TypedModelMeta):
        proxy = True

    objects: TeacherUserManager[  # type: ignore[misc]
        "TeacherUser"
    ] = TeacherUserManager()  # type: ignore[assignment]


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class SchoolTeacherUserManager(TeacherUserManager[AnyUser], t.Generic[AnyUser]):
    # pylint: disable-next=signature-differs,too-many-arguments
    def create_user(  # type: ignore[override]
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        school: School,
        is_admin: bool = False,
        is_verified: bool = False,
        **extra_fields,
    ):
        return super().create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            school=school,
            is_admin=is_admin,
            is_verified=is_verified,
            **extra_fields,
        )

    def filter_users(self, queryset: QuerySet[User]):
        return (
            super()
            .filter_users(queryset)
            .filter(new_teacher__school__isnull=False)
        )


# pylint: disable-next=too-many-ancestors
class SchoolTeacherUser(TeacherUser):
    """A user that is a teacher in a school."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: SchoolTeacherUserManager[  # type: ignore[misc]
        "SchoolTeacherUser"
    ] = SchoolTeacherUserManager()  # type: ignore[assignment]

    @property
    def teacher(self):
        # pylint: disable-next=import-outside-toplevel
        from .teacher import SchoolTeacher, teacher_as_type

        teacher = super().teacher

        return teacher_as_type(teacher, SchoolTeacher) if teacher else None


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class AdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["AdminSchoolTeacherUser"]
):
    def filter_users(self, queryset: QuerySet[User]):
        return super().filter_users(queryset).filter(new_teacher__is_admin=True)


# pylint: disable-next=too-many-ancestors
class AdminSchoolTeacherUser(SchoolTeacherUser):
    """A user that is an admin-teacher in a school."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: AdminSchoolTeacherUserManager = (  # type: ignore[misc]
        AdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        # pylint: disable-next=import-outside-toplevel
        from .teacher import AdminSchoolTeacher, teacher_as_type

        teacher = super().teacher

        return teacher_as_type(teacher, AdminSchoolTeacher) if teacher else None


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonAdminSchoolTeacherUserManager(
    SchoolTeacherUserManager["NonAdminSchoolTeacherUser"]
):
    def filter_users(self, queryset: QuerySet[User]):
        return (
            super().filter_users(queryset).filter(new_teacher__is_admin=False)
        )


# pylint: disable-next=too-many-ancestors
class NonAdminSchoolTeacherUser(SchoolTeacherUser):
    """A user that is a non-admin-teacher in a school."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonAdminSchoolTeacherUserManager = (  # type: ignore[misc]
        NonAdminSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        # pylint: disable-next=import-outside-toplevel
        from .teacher import NonAdminSchoolTeacher, teacher_as_type

        teacher = super().teacher

        return (
            teacher_as_type(teacher, NonAdminSchoolTeacher) if teacher else None
        )


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class NonSchoolTeacherUserManager(TeacherUserManager["NonSchoolTeacherUser"]):
    def filter_users(self, queryset: QuerySet[User]):
        return (
            super()
            .filter_users(queryset)
            .filter(new_teacher__school__isnull=True)
        )


# pylint: disable-next=too-many-ancestors
class NonSchoolTeacherUser(TeacherUser):
    """A user that is a teacher not in a school."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: NonSchoolTeacherUserManager = (  # type: ignore[misc]
        NonSchoolTeacherUserManager()  # type: ignore[assignment]
    )

    @property
    def teacher(self):
        # pylint: disable-next=import-outside-toplevel
        from .teacher import NonSchoolTeacher, teacher_as_type

        teacher = super().teacher

        return teacher_as_type(teacher, NonSchoolTeacher) if teacher else None


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class StudentUserManager(UserManager["StudentUser"]):
    def create_user(  # type: ignore[override]
        self, first_name: str, klass: Class, **extra_fields
    ):
        """Create a student-user."""
        # pylint: disable-next=import-outside-toplevel
        from .student import Student

        # pylint: disable=protected-access
        password = StudentUser._get_random_password()
        login_id, hashed_login_id = StudentUser._get_random_login_id()
        # pylint: enable=protected-access

        user = super().create_user(
            **extra_fields,
            first_name=first_name,
            username=StudentUser.get_random_username(),
            password=password,
        )

        Student.objects.create(
            class_field=klass,
            user=UserProfile.objects.create(user=user),
            new_user=user,
            login_id=hashed_login_id,
        )

        # pylint: disable=protected-access
        user._password = password
        user._login_id = login_id
        # pylint: enable=protected-access

        # TODO: delete this in new data schema
        TotalActivity.objects.update(
            student_registrations=F("student_registrations") + 1
        )

        return user

    def filter_users(self, queryset: QuerySet[User]):
        return queryset.filter(
            new_teacher__isnull=True,
            new_student__isnull=False,
            # TODO: remove in new model
            new_student__class_field__isnull=False,
        )

    def get_queryset(self):
        return super().get_queryset().prefetch_related("new_student")


# pylint: disable-next=too-many-ancestors
class StudentUser(User):
    """A user that is a student."""

    # TODO: move this is to Student model in new schema.
    _login_id: t.Optional[str]

    teacher: None
    student: "Student"

    credential_fields = frozenset(["first_name", "password"])

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
        # pylint: disable-next=import-outside-toplevel
        # from .student import Student

        # login_id = None
        # while (
        #     login_id is None
        #     or Student.objects.filter(login_id=login_id).exists()
        # ):
        #     login_id = get_random_string(length=64)

        # TODO: replace below code with commented out code above.
        # pylint: disable-next=import-outside-toplevel
        from common.helpers.generators import generate_login_id

        return generate_login_id()

    @staticmethod
    def get_random_username():
        """Generate a random username that is unique."""
        username = None
        while (
            username is None or User.objects.filter(username=username).exists()
        ):
            username = get_random_string(length=30)

        return username

    # pylint: disable-next=arguments-differ
    def set_password(self, raw_password: t.Optional[str] = None):
        super().set_password(raw_password or self._get_random_password())
        self._login_id, self.student.login_id = self._get_random_login_id()


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class IndependentUserManager(ContactableUserManager["IndependentUser"]):
    def filter_users(self, queryset: QuerySet[User]):
        return (
            super()
            .filter_users(queryset)
            .filter(
                new_teacher__isnull=True,
                # TODO: student__isnull=True in new model
                new_student__isnull=False,
                new_student__class_field__isnull=True,
            )
        )

    def get_queryset(self):
        return super().get_queryset().prefetch_related("new_student")

    def create_user(  # type: ignore[override]
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        **extra_fields,
    ):
        """Create an independent-user."""
        # pylint: disable-next=import-outside-toplevel
        from .student import Student

        assert "username" not in extra_fields

        user = super().create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )

        # NOTE: Indy user needs a student object for now while we use the
        # old models.
        # TODO: Remove this once using the new models.
        Student.objects.create(
            new_user=user,
            user=UserProfile.objects.create(user=user),
        )

        # TODO: delete this in new data schema
        TotalActivity.objects.update(
            independent_registrations=F("independent_registrations") + 1
        )

        return user


# pylint: disable-next=too-many-ancestors
class IndependentUser(ContactableUser):
    """A user that is an independent learner."""

    teacher: None
    student: "Independent"  # TODO: set to None in new model

    class Meta(TypedModelMeta):
        proxy = True

    objects: IndependentUserManager = (  # type: ignore[misc]
        IndependentUserManager()  # type: ignore[assignment]
    )


# pylint: disable-next=invalid-name
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
