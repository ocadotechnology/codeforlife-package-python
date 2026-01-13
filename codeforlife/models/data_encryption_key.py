import typing as t

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from tink import (  # type: ignore[import-untyped]
    BinaryKeysetReader,
    read_keyset_handle,
)
from tink.aead import Aead  # type: ignore[import-untyped]
from tink.integration.gcpkms import GcpKmsClient  # type: ignore[import-untyped]

from .base import Model

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class DataEncryptionKeyModel(Model):
    """Base model for models that store encrypted DEKs."""

    dek = models.BinaryField(
        verbose_name=_("data encryption key"),
        help_text=_("The encrypted data encryption key (DEK) for this model."),
        editable=False,
    )

    class Meta(TypedModelMeta):
        abstract = True

    def _get_master_key_aead(self):
        """Gets the AEAD primitive for the KMS master key."""
        return GcpKmsClient(
            settings.KMS_MASTER_KEY_URI, settings.KMS_CREDENTIALS_PATH
        ).get_aead(settings.KMS_MASTER_KEY_URI)

    @property
    def dek_aead(self):
        if not self.dek:
            raise ValueError("The data encryption key (DEK) is missing.")

        dek_aead = read_keyset_handle(
            keyset_reader=BinaryKeysetReader(self.dek),
            master_key_aead=self._get_master_key_aead(),
        ).primitive(Aead)

        return dek_aead  # TODO: Cache this value.
