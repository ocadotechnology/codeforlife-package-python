"""
© Ocado Group
Created on 19/01/2026 at 09:55:44(+00:00).

Here we provide a few utility functions that interact with Google Cloud KMS and
the `tink` cryptography library.

To avoid a dependency on Google Cloud KMS during local development and in CI/CD
pipelines, we use fake (mock) implementations of the KMS client and its AEAD
primitive. A simple check for the environment (e.g., `settings.ENV == "local"`)
determines whether to use the real `GcpKmsClient` or a `FakeGcpKmsClient`.

The fake client mimics the behavior of the real one. Instead of performing real
encryption, it simulates it by encoding the plaintext in base64 and adding a
prefix. This allows the application to run without needing cloud credentials
while still being able to distinguish between "encrypted" and plaintext data.

While the `FakeAead` and `FakeGcpKmsClient` are sufficient for running a local
development server, they are not `unittest.mock.MagicMock` instances by default.
This is intentional, as we don't want the overhead of tracking function calls
during local development.

For unit tests, where you might need to assert that encryption or decryption
methods were called, both fake classes provide an `as_mock()` class method. This
method returns a `MagicMock` instance of the class, allowing you to use mock
assertions like `assert_called_once()`.
"""

import typing as t
from base64 import b64decode, b64encode
from dataclasses import dataclass
from io import BytesIO
from unittest.mock import MagicMock, create_autospec

from django.conf import settings
from django.utils.crypto import get_random_string
from tink import (  # type: ignore[import-untyped]
    BinaryKeysetReader,
    BinaryKeysetWriter,
    new_keyset_handle,
    read_keyset_handle,
)
from tink.aead import Aead, aead_key_templates  # type: ignore[import-untyped]
from tink.aead import register as aead_register  # type: ignore[import-untyped]
from tink.integration import gcpkms  # type: ignore[import-untyped]

# Shortcut to the real GcpKmsClient class.
_GcpKmsClient = gcpkms.GcpKmsClient


@dataclass
class FakeAead:
    """A fake AEAD primitive for local testing."""

    @staticmethod
    # pylint: disable-next=unused-argument
    def encrypt(plaintext: bytes, associated_data: bytes = b""):
        """Simulate ciphertext by wrapping in base64 and adding a prefix."""
        return b"fake_enc:" + b64encode(plaintext)

    @staticmethod
    # pylint: disable-next=unused-argument
    def decrypt(ciphertext: bytes, associated_data: bytes = b""):
        """Simulate decryption by removing prefix and base64 decoding."""
        if not ciphertext.startswith(b"fake_enc:"):
            raise ValueError("Invalid ciphertext for fake mock")

        return b64decode(ciphertext.replace(b"fake_enc:", b""))

    @classmethod
    def as_mock(cls):
        """
        Returns the class as a functional MagicMock for testing. The mock tracks
        calls while still performing the fake encryption and decryption by using
        the original methods as side effects. We set `instance=True` to ensure
        the mock behaves as an instance of the class, not the class itself.
        """
        mock: MagicMock = create_autospec(Aead, instance=True)
        mock.encrypt.side_effect = cls.encrypt
        mock.decrypt.side_effect = cls.decrypt

        return mock


@dataclass
class FakeGcpKmsClient:
    """A fake GcpKmsClient for local testing."""

    key_uri: str

    @staticmethod
    def register_client(
        key_uri: t.Optional[str], credentials_path: t.Optional[str]
    ):
        """No-op for registering the fake client."""

    # pylint: disable-next=unused-argument
    def get_aead(self, key_uri: str) -> Aead:
        """Return the fake AEAD primitive."""
        return FakeAead()

    @classmethod
    def as_mock(cls):
        """
        Returns the class as a functional MagicMock for testing. It returns a
        mocked FakeAead instance that is also functional. We set `instance=True`
        to ensure the mock behaves as an instance of the class, not the class
        itself.
        """
        mock: MagicMock = create_autospec(_GcpKmsClient, instance=True)
        mock.get_aead.return_value = FakeAead.as_mock()

        return mock


def _get_kek_aead():
    """Get the AEAD primitive for the key encryption key (KEK)."""
    return GcpKmsClient(key_uri=settings.GCP_KMS_KEY_URI).get_aead(
        key_uri=settings.GCP_KMS_KEY_URI
    )


def create_dek():
    """
    Creates a new random AES-256-GCM data encryption key (DEK), wraps it with
    Cloud KMS, and returns the binary blob for storage.
    """
    # In local environment, return a fake encrypted DEK.
    if settings.ENV == "local":
        return FakeAead.encrypt(get_random_string(32).encode())

    stream = BytesIO()
    new_keyset_handle(key_template=aead_key_templates.AES256_GCM).write(
        keyset_writer=BinaryKeysetWriter(stream),
        master_key_primitive=_get_kek_aead(),
    )

    return stream.getvalue()


def get_dek_aead(dek: bytes) -> Aead:
    """
    Takes an encrypted DEK, decrypts it with the KEK, and returns the AEAD
    primitive for performing cryptographic operations.
    """
    if not dek:
        raise ValueError("The data encryption key (DEK) is missing.")

    # In local environment, return the fake AEAD primitive.
    if settings.ENV == "local":
        return FakeAead()

    return read_keyset_handle(
        keyset_reader=BinaryKeysetReader(dek),
        master_key_aead=_get_kek_aead(),
    ).primitive(Aead)


# Ensure Tink AEAD is registered.
aead_register()

# Use the fake client in 'local' environment, otherwise use the real one.
GcpKmsClient = FakeGcpKmsClient if settings.ENV == "local" else _GcpKmsClient

# Register the GCP KMS client with Tink.
GcpKmsClient.register_client(
    key_uri=settings.GCP_KMS_KEY_URI, credentials_path=None
)
