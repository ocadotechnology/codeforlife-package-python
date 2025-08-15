"""
© Ocado Group
Created on 12/08/2025 at 10:28:24(+01:00).
"""

import typing as t

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class EncryptedCharField(models.CharField):
    """
    A custom CharField that encrypts data before saving and decrypts it when
    retrieved.
    """

    _fernet = Fernet(settings.SECRET_KEY)
    _prefix = "ENC:"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] += len(self._prefix)
        super().__init__(*args, **kwargs)

    # pylint: disable-next=unused-argument
    def from_db_value(self, value: t.Optional[str], expression, connection):
        """
        Converts a value as returned by the database to a Python object. It is
        the reverse of get_prep_value().

        https://docs.djangoproject.com/en/5.1/howto/custom-model-fields/#converting-values-to-python-objects
        """
        if isinstance(value, str):
            return self.decrypt_value(value)
        return value

    def to_python(self, value: t.Optional[str]):
        """
        Converts the value into the correct Python object. It acts as the
        reverse of value_to_string(), and is also called in clean().

        https://docs.djangoproject.com/en/5.1/howto/custom-model-fields/#converting-values-to-python-objects
        """
        if isinstance(value, str):
            return self.decrypt_value(value)
        return value

    def get_prep_value(self, value: t.Optional[str]):
        """
        'value' is the current value of the model's attribute, and the method
        should return data in a format that has been prepared for use as a
        parameter in a query.

        https://docs.djangoproject.com/en/5.1/howto/custom-model-fields/#converting-python-objects-to-query-values
        """
        if isinstance(value, str):
            return self.encrypt_value(value)
        return value

    def encrypt_value(self, value: str):
        """Encrypt the value if it's not encrypted."""
        if not value.startswith(self._prefix):
            return self._prefix + self._fernet.encrypt(value.encode()).decode()
        return value

    def decrypt_value(self, value: str):
        """Decrpyt the value if it's encrypted.."""
        if value.startswith(self._prefix):
            value = value[len(self._prefix) :]
            return self._fernet.decrypt(value).decode()
        return value
