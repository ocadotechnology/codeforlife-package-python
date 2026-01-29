"""
© Ocado Group
Created on 29/01/2026 at 14:03:09(+00:00).
"""

import typing as t

from .base_data_encryption_key import BaseDataEncryptionKeyModel
from .fields import DataEncryptionKeyField

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class DataEncryptionKeyModel(BaseDataEncryptionKeyModel):
    """A model that includes a data encryption key field."""

    # Create a DataEncryptionKeyField to store the encrypted DEK.
    dek: DataEncryptionKeyField = DataEncryptionKeyField()

    class Meta(TypedModelMeta):
        abstract = True
