import typing as t

from django.contrib.auth.backends import BaseBackend

from ....request import WSGIRequest
from ...models import AuthFactor, User


class TokenBackend(BaseBackend):
    def authenticate(
        self,
        request: WSGIRequest,
        token: t.Optional[str] = None,
        **kwargs,
    ):
        if (
            token is None
            or not isinstance(request.user, User)
            or not request.user.session.session_auth_factors.filter(
                auth_factor__type=AuthFactor.Type.OTP
            ).exists()
        ):
            return

        for backup_token in request.user.backup_tokens.all():
            if backup_token.check_token(token):
                # Delete OTP auth factor from session.
                request.user.session.session_auth_factors.filter(
                    auth_factor__type=AuthFactor.Type.OTP
                ).delete()

                return request.user

    def get_user(self, user_id: int):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
