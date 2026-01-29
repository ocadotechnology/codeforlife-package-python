"""
© Ocado Group
Created on 26/01/2026 at 10:32:18(+00:00).
"""

import typing as t

from cachetools import TTLCache
from django.core.exceptions import ValidationError

from ..encryption import get_dek_aead
from .encrypted import EncryptedModel

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta

    from .fields import DataEncryptionKeyField
else:
    TypedModelMeta = object


class BaseDataEncryptionKeyModel(EncryptedModel):
    """Model to store data encryption keys."""

    # Cache configuration for data encryption keys.
    dek_aead_cache_maxsize: float = 1024
    dek_aead_cache_ttl: float = 900  # 15 minutes

    DEK_AEAD_CACHE: TTLCache

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.DEK_AEAD_CACHE = TTLCache(
            maxsize=cls.dek_aead_cache_maxsize, ttl=cls.dek_aead_cache_ttl
        )

    # Reference to the DataEncryptionKeyField.
    _dek: t.Optional["DataEncryptionKeyField"] = None

    class Meta(TypedModelMeta):
        abstract = True

    @property
    def dek_aead(self):
        # Return None if there is no DEK.
        if self._dek is None:
            return None

        # Ensure the instance is saved before accessing the DEK AEAD.
        if self.pk is None:
            raise ValidationError(
                "Instance must be saved before accessing dek_aead.",
                code="unsaved_instance",
            )

        # Check the cache for the DEK AEAD.
        if self.pk in self.DEK_AEAD_CACHE:
            return self.DEK_AEAD_CACHE[self.pk]

        # Get the AEAD primitive for the data encryption key.
        dek_aead = get_dek_aead(self._dek)

        # Cache the DEK AEAD for future access.
        self.DEK_AEAD_CACHE[self.pk] = dek_aead

        return dek_aead
