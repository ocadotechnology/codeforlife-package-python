# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t

from common.models import UserProfile
from django.db.models.query import QuerySet

from .contactable import ContactableUser, ContactableUserManager
from .user import User

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class GoogleUserManager(ContactableUserManager[AnyUser], t.Generic[AnyUser]):
    # pylint: disable-next=too-many-arguments
    def sync(  # type: ignore[override]
        self,
        first_name: str,
        last_name: str,
        email: str,
        is_verified: bool,
        refresh_token: str,
    ):
        """Sync a Google-user."""

        email = email.lower()

        try:
            user = super().get(email=email)

            user.first_name = first_name
            user.last_name = last_name
            user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                ]
            )

            user.userprofile.is_verified = is_verified
            user.userprofile.save(update_fields=["is_verified"])
        except GoogleUser.DoesNotExist:
            user = super().create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )

            UserProfile.objects.create(
                user=user,
                is_verified=is_verified,
                google_refresh_token=refresh_token,
            )

        return user

    def filter_users(self, queryset: QuerySet[User]):
        return super().filter_users(queryset)  # TODO


# pylint: disable-next=too-many-ancestors
class GoogleUser(ContactableUser):
    """A user that has linked their Google Account."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: GoogleUserManager[  # type: ignore[misc]
        "GoogleUser"
    ] = GoogleUserManager()  # type: ignore[assignment]
