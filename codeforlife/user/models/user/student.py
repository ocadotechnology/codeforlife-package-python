# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import string
import typing as t

from common.models import TotalActivity, UserProfile
from django.db.models import F
from django.db.models.query import QuerySet
from django.utils.crypto import get_random_string

from ..klass import Class
from .user import User, UserManager

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta

    from ..student import Student
else:
    TypedModelMeta = object

AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class StudentUserManager(UserManager["StudentUser"]):
    def create_user(  # type: ignore[override]
        self, first_name: str, klass: Class, **extra_fields
    ):
        """Create a student-user."""
        # pylint: disable-next=import-outside-toplevel
        from ..student import Student

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
        # from ..student import Student

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
