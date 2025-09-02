# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t

from common.models import UserProfile
from django.db.models.query import QuerySet
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ....types import JsonDict
from .contactable import ContactableUser, ContactableUserManager
from .user import User

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring,too-few-public-methods
class GoogleUserManager(ContactableUserManager[AnyUser], t.Generic[AnyUser]):
    def __init__(self):
        super().__init__()

        self.session = Session()
        self.session.mount(
            prefix="https://",
            adapter=HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.1)),
        )

    def _sync(self, auth_header: str, refresh_token: t.Optional[str] = None):
        response = self.session.get(
            url="https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": auth_header},
            timeout=10,
        )
        response.raise_for_status()

        user_data: JsonDict = response.json()
        email = t.cast(str, user_data["email"]).lower()
        is_verified = t.cast(bool, user_data["email_verified"])
        first_name = t.cast(str, user_data["given_name"])
        last_name = t.cast(str, user_data["family_name"])
        google_sub = t.cast(str, user_data["sub"])

        try:
            user = self.get(userprofile__google_sub=google_sub)

            user.username = email
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save(
                update_fields=[
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                ]
            )

            user.userprofile.is_verified = is_verified
            user.userprofile.save(update_fields=["is_verified"])
        except GoogleUser.DoesNotExist as does_not_exist:
            if not refresh_token:
                raise does_not_exist

            user = self.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )

            UserProfile.objects.create(
                user=user,
                is_verified=is_verified,
                google_refresh_token=refresh_token,
                google_sub=google_sub,
            )

        return user

    # pylint: disable-next=redefined-builtin
    def sync(self, id: int):
        """Syncs an existing Google-user."""
        # NOTE: Avoids circular dependencies.
        # pylint: disable-next=import-outside-toplevel,cyclic-import
        from ...caches import GoogleOAuth2TokenCache

        return self._sync(
            auth_header=GoogleOAuth2TokenCache.get_auth_header(id)
        )

    def sync_or_create(self, auth_header: str, refresh_token: str):
        """Syncs an existing Google-user or creates a new one."""
        return self._sync(auth_header=auth_header, refresh_token=refresh_token)

    def filter_users(self, queryset: QuerySet[User]):
        return (
            super()
            .filter_users(queryset)
            .exclude(userprofile__google_refresh_token__isnull=True)
            .exclude(userprofile__google_refresh_token="")
            .exclude(userprofile__google_sub__isnull=True)
            .exclude(userprofile__google_sub="")
        )


# pylint: disable-next=too-many-ancestors
class GoogleUser(ContactableUser):
    """A user that has linked their Google Account."""

    class Meta(TypedModelMeta):
        proxy = True

    objects: GoogleUserManager[  # type: ignore[misc]
        "GoogleUser"
    ] = GoogleUserManager()  # type: ignore[assignment]

    def sync(self):
        """Syncs current user with Google."""
        GoogleUser.objects.sync(self.id)
        self.refresh_from_db()
