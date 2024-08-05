"""
© Ocado Group
Created on 05/08/2024 at 08:39:57(+01:00).
"""

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest

from ..user.models import User


class BaseLoginForm(forms.Form):
    """
    Base login form that all other login forms must inherit.
    """

    user: User

    def __init__(self, request: WSGIRequest, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        """Authenticates a user.

        Raises:
            ValidationError: If there are form errors.
            ValidationError: If the user's credentials were incorrect.
            ValidationError: If the user's account is deactivated.

        Returns:
            The cleaned form data.
        """

        if self.errors:
            raise ValidationError(
                "Found form errors. Skipping authentication.",
                code="form_errors",
            )

        user = authenticate(
            self.request,
            **{key: self.cleaned_data[key] for key in self.fields.keys()}
        )
        if user is None:
            raise ValidationError(
                self.get_invalid_login_error_message(),
                code="invalid_login",
            )
        if not isinstance(user, User):
            raise ValidationError(
                "Incorrect user class.",
                code="incorrect_user_class",
            )
        self.user = user

        if not user.is_active:
            raise ValidationError(
                "User is not active",
                code="user_not_active",
            )

        return self.cleaned_data

    def get_invalid_login_error_message(self) -> str:
        """Returns the error message if the user failed to login.

        Raises:
            NotImplementedError: If message is not set.
        """
        raise NotImplementedError()
