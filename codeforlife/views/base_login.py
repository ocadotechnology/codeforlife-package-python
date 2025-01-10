"""
© Ocado Group
Created on 07/11/2024 at 14:58:38(+00:00).
"""

import json
import typing as t
from urllib.parse import quote_plus

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from rest_framework import status

from ..forms import BaseLoginForm
from ..models import AbstractBaseUser
from ..request import BaseHttpRequest
from ..types import CookieSamesite, JsonDict

AnyBaseHttpRequest = t.TypeVar("AnyBaseHttpRequest", bound=BaseHttpRequest)
AnyAbstractBaseUser = t.TypeVar("AnyAbstractBaseUser", bound=AbstractBaseUser)


class BaseLoginView(
    LoginView,
    t.Generic[AnyBaseHttpRequest, AnyAbstractBaseUser],
):
    """
    Extends Django's login view to allow a user to log in using one of the
    approved forms.

    WARNING: It's critical that to inherit Django's login view as it implements
        industry standard security measures that a login view should have.
    """

    request: AnyBaseHttpRequest

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["data"] = json.loads(self.request.body)

        return form_kwargs

    def get_session_metadata(self, user: AnyAbstractBaseUser) -> JsonDict:
        """Get the session's metadata.

        Args:
            user: The user the session is for.

        Raises:
            NotImplementedError: If this method is not implemented.

        Returns:
            A JSON-serializable dict containing the session's metadata.
        """
        raise NotImplementedError

    def form_valid(
        self, form: BaseLoginForm[AnyAbstractBaseUser]  # type: ignore
    ):
        user = form.user

        # Clear expired sessions.
        self.request.session.clear_expired(user_id=user.pk)

        # Create session (without data).
        login(self.request, user)

        # Save session (with data).
        self.request.session.save()

        # Get session metadata.
        session_metadata = self.get_session_metadata(user)

        # Return session metadata in response and a non-HTTP-only cookie.
        response = JsonResponse(session_metadata)
        response.set_cookie(
            key=settings.SESSION_METADATA_COOKIE_NAME,
            value=quote_plus(
                json.dumps(
                    session_metadata,
                    separators=(",", ":"),
                    indent=None,
                )
            ),
            max_age=(  # Expires when the session cookie expires.
                None
                if settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
                else settings.SESSION_COOKIE_AGE
            ),
            path=settings.SESSION_METADATA_COOKIE_PATH,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=t.cast(
                CookieSamesite, settings.SESSION_METADATA_COOKIE_SAMESITE
            ),
            domain=settings.SESSION_METADATA_COOKIE_DOMAIN,
            httponly=False,
        )

        return response

    def form_invalid(
        self, form: BaseLoginForm[AnyAbstractBaseUser]  # type: ignore
    ):
        return JsonResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)
