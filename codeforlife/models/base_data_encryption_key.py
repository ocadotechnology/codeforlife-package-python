"""
© Ocado Group
Created on 26/01/2026 at 10:32:18(+00:00).

This abstract model brings the `EncryptedModel` and `DataEncryptionKeyField`
together. It also implements the `dek_aead` property, which retrieves and caches
the decrypted DEK's AEAD primitive for use in encryption/decryption operations.
"""

import typing as t

from cachetools import TTLCache
from django.core.exceptions import ValidationError

from ..encryption import create_dek, get_dek_aead
from .encrypted import EncryptedModel

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta

    from .fields.data_encryption_key import Dek
else:
    TypedModelMeta = object


class BaseDataEncryptionKeyModel(EncryptedModel):
    """Model to store and manage a data encryption key."""

    # Cache configuration for data encryption keys.
    dek_aead_cache_maxsize: float = 1024
    dek_aead_cache_ttl: float = 900  # 15 minutes

    # In-memory cache for the decrypted DEK AEAD primitive.
    DEK_AEAD_CACHE: TTLCache

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.DEK_AEAD_CACHE = TTLCache(
            maxsize=cls.dek_aead_cache_maxsize, ttl=cls.dek_aead_cache_ttl
        )

    # A class-level reference to the DataEncryptionKeyField instance.
    # This is set by the `contribute_to_class` method of the field.
    DEK_FIELD: t.Optional[str] = None

    class Meta(TypedModelMeta):
        abstract = True

    @property
    def dek_aead(self):
        """
        Provides the AEAD primitive for the DEK, caching it for performance.
        """
        # Ensure the instance is saved before accessing the DEK AEAD.
        if self.pk is None:
            raise ValidationError(
                "Instance must be saved before accessing dek_aead.",
                code="unsaved_instance",
            )

        # Return None if there is no DEK field.
        if self.DEK_FIELD is None:
            return None

        # Get the DEK and return None if it's not set.
        dek: t.Optional["Dek"] = getattr(self, self.DEK_FIELD)
        if dek is None:
            return None

        # Check the cache for the DEK AEAD.
        if self.pk in self.DEK_AEAD_CACHE:
            return self.DEK_AEAD_CACHE[self.pk]

        # Get the AEAD primitive for the data encryption key.
        dek_aead = get_dek_aead(bytes(dek))

        # Cache the DEK AEAD for future access.
        self.DEK_AEAD_CACHE[self.pk] = dek_aead

        return dek_aead

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        # Lazily create a new DEK for new instances.
        if (
            self.pk is None
            and self.DEK_FIELD is not None
            and getattr(self, self.DEK_FIELD) is None
        ):
            self.__dict__[self.DEK_FIELD] = create_dek()

        # pylint: disable=duplicate-code
        return super().save(  # type: ignore[misc]
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
        # pylint: enable=duplicate-code
