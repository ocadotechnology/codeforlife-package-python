# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t

from common.models import TotalActivity, UserProfile
from django.db.models import F
from django.db.models.query import QuerySet

from ..school import School
from .contactable import ContactableUser, ContactableUserManager
from .user import User

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta

    from ..teacher import Teacher
else:
    TypedModelMeta = object

AnyUser = t.TypeVar("AnyUser", bound=User)


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
        from ..teacher import Teacher

        assert "username" not in extra_fields

        # pylint: disable=duplicate-code
        user = super().create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        # pylint: enable=duplicate-code

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
