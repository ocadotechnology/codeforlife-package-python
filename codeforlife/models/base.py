"""
© Ocado Group
Created on 19/01/2024 at 15:18:48(+00:00).

Base model for all Django models.
"""

import typing as t

from django.db import models

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
    from tink.aead import Aead

    from .encrypted_text_field import EncryptedTextField
else:
    TypedModelMeta = object


# class Manager(models.Manager["AnyModel"], t.Generic["AnyModel"]):
#     """Base manager for all models."""

#     def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
#         """
#         Intercepts bulk_create to encrypt data in memory before saving.
#         """
#         for obj in objs:
#             if hasattr(obj, "ensure_key_exists"):
#                 obj.ensure_key_exists()
#             if hasattr(obj, "encrypt_all_fields"):
#                 obj.encrypt_all_fields()

#         return super().bulk_create(
#             objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts
#         )

#     def update(self, **kwargs):
#         """
#         Block standard update() on encrypted fields because it bypasses the
#         per-row unique keys.
#         """
#         if hasattr(self.model, "ENCRYPTED_FIELDS"):
#             if any(field in kwargs for field in self.model.ENCRYPTED_FIELDS):
#                 raise NotImplementedError(
#                     "Cannot use .update() on encrypted fields. "
#                     "Use .bulk_update() or iterate and save() instead."
#                 )

#         return super().update(**kwargs)


class Model(models.Model):
    """Base for all models."""

    ASSOCIATED_DATA: str
    _ENCRYPTED_FIELDS: t.List["EncryptedTextField"] = []

    objects: models.Manager[t.Self]  # = Manager()

    class Meta(TypedModelMeta):
        abstract = True

    @property
    def dek_aead(self) -> "Aead":
        """Gets the AEAD primitive for this model's DEK."""
        raise NotImplementedError()

    def encrypt_all_fields(self):
        """
        Helper called by Manager.bulk_create().
        Forces the encryption of all properties into their DB fields.
        """
        for field in self._ENCRYPTED_FIELDS:
            plaintext = getattr(
                self, field.name, None
            )  # field.getter_and_setter.fget(self)
            if plaintext:
                # The setter on the property will handle encryption
                setattr(self, field.name, plaintext)


AnyModel = t.TypeVar("AnyModel", bound=Model)
