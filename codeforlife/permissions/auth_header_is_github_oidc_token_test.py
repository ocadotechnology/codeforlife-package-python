"""
© Ocado Group
Created on 19/06/2025 at 11:30:00(+00:00).
"""

import base64
from datetime import timedelta
from unittest.mock import patch

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.utils import timezone

from ..tests import PermissionTestCase
from ..user.models import User
from .auth_header_is_github_oidc_token import AuthHeaderIsGitHubOidcToken


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class TestAuthHeaderIsGitHubOidcToken(
    PermissionTestCase[AuthHeaderIsGitHubOidcToken, User]
):
    permission_class = AuthHeaderIsGitHubOidcToken
    request_user_class = User

    def test_eq(self):
        """Successfully equates two instances."""
        self.assert_eq(kwargs1={"jwks_ttl": 1}, kwargs2={"jwks_ttl": 2})

    def test_has_permission(self):
        """Successfully decodes an GitHub OIDC token set in the auth header."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        pem_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        public_key = private_key.public_key()
        public_numbers = public_key.public_numbers()
        pem_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        n_b64url = (
            base64.urlsafe_b64encode(
                public_numbers.n.to_bytes(
                    (public_numbers.n.bit_length() + 7) // 8, "big"
                )
            )
            .decode("utf-8")
            .rstrip("=")
        )
        e_b64url = (
            base64.urlsafe_b64encode(
                public_numbers.e.to_bytes(
                    (public_numbers.e.bit_length() + 7) // 8, "big"
                )
            )
            .decode("utf-8")
            .rstrip("=")
        )

        rsa_public_jwk = {
            "kty": "RSA",
            "use": "sig",
            "kid": pem_public_key,
            "alg": "RS256",
            "n": n_b64url,
            "e": e_b64url,
        }

        with patch.object(
            AuthHeaderIsGitHubOidcToken,
            "_get_jwks",
            return_value=[rsa_public_jwk],
        ):

            self.assert_has_permission(
                has_permission=True,
                request=self.request_factory.get(
                    headers={
                        "Authorization": "Bearer "
                        + jwt.encode(
                            {
                                "exp": timezone.now() + timedelta(days=1),
                                "aud": [settings.SERVICE_DOMAIN],
                                "iss": AuthHeaderIsGitHubOidcToken.issuer,
                            },
                            key=pem_private_key,
                            algorithm="RS256",
                            headers=rsa_public_jwk,
                        )
                    },
                ),
            )
