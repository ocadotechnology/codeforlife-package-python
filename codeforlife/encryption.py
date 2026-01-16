import typing as t
from base64 import b64decode, b64encode
from dataclasses import dataclass
from io import BytesIO
from unittest.mock import MagicMock, create_autospec

from django.conf import settings
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
    def encrypt(plaintext: bytes, associated_data: bytes):
        """Simulate ciphertext by wrapping in base64 and adding a prefix."""
        return b"fake_enc:" + b64encode(plaintext)

    @staticmethod
    # pylint: disable-next=unused-argument
    def decrypt(ciphertext: bytes, associated_data: bytes):
        """Simulate decryption by removing prefix and base64 decoding."""
        if not ciphertext.startswith(b"fake_enc:"):
            raise ValueError("Invalid ciphertext for fake mock")

        return b64decode(ciphertext.replace(b"fake_enc:", b""))

    @classmethod
    def as_mock(cls):
        """Factory method to build the mock AEAD."""
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
        """Factory method to build the mock GcpKmsClient."""
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
    stream = BytesIO()
    new_keyset_handle(key_template=aead_key_templates.AES256_GCM).write(
        keyset_writer=BinaryKeysetWriter(stream),
        master_key_primitive=_get_kek_aead(),
    )

    return stream.getvalue()


def get_dek_aead(dek: bytes) -> Aead:
    """Get the AEAD primitive for the given data encryption key (DEK)."""
    if not dek:
        raise ValueError("The data encryption key (DEK) is missing.")

    return read_keyset_handle(
        keyset_reader=BinaryKeysetReader(dek),
        master_key_aead=_get_kek_aead(),
    ).primitive(Aead)


# Ensure Tink AEAD is registered.
aead_register()

# Get the GcpKmsClient class depending on the environment.
GcpKmsClient = FakeGcpKmsClient if settings.ENV == "local" else _GcpKmsClient

# Register the GCP KMS client.
GcpKmsClient.register_client(
    key_uri=settings.GCP_KMS_KEY_URI, credentials_path=None
)
