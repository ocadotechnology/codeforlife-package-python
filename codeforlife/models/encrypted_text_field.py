"""
© Ocado Group
Created on 12/01/2026 at 09:17:46(+00:00).
"""

from .base_encrypted_field import BaseEncryptedField


class EncryptedTextField(BaseEncryptedField[str]):
    """An encrypted text field."""

    def bytes_to_value(self, data):
        return data.decode()

    def value_to_bytes(self, value):
        return value.encode()
