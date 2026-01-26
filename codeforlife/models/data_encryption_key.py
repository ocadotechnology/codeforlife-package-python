"""
© Ocado Group
Created on 26/01/2026 at 10:32:18(+00:00).
"""

import typing as t

from ..encryption import get_dek_aead
from .base import Model
from .fields import DataEncryptionKeyField

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class DataEncryptionKeyModel(Model):
    """Model to store data encryption keys."""

    # Create a DataEncryptionKeyField to store the encrypted DEK.
    dek: DataEncryptionKeyField = DataEncryptionKeyField()

    class Meta(TypedModelMeta):
        abstract = True

    @property
    def dek_aead(self):
        """Return the AEAD primitive for the data encryption key."""
        # TODO: Cache this value.
        return get_dek_aead(self.dek) if self.dek else None
