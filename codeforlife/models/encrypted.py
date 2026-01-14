import typing as t

from django.core.exceptions import ValidationError
from django.db import models

from .base import Model

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
    from tink.aead import Aead

    from .base_encrypted_field import BaseEncryptedField
else:
    TypedModelMeta = object


class _EncryptedModel(Model):
    ENCRYPTED_FIELDS: t.List["BaseEncryptedField"] = []

    associated_data: str

    class Meta(TypedModelMeta):
        abstract = True


AnyEncryptedModel = t.TypeVar("AnyEncryptedModel", bound=_EncryptedModel)


class EncryptedModel(_EncryptedModel):
    """Base for all models with encrypted fields."""

    def __init__(self, **kwargs):
        for name in kwargs:
            if any(field.name == name for field in self.ENCRYPTED_FIELDS):
                raise ValidationError(
                    f"Cannot set encrypted field '{name}' via __init__."
                    " Set the property after initialization instead.",
                    code="cannot_set_encrypted_field",
                )

        super().__init__(**kwargs)

    class Manager(
        models.Manager[AnyEncryptedModel], t.Generic[AnyEncryptedModel]
    ):
        """Base manager for models with encrypted fields."""

        def update(self, **kwargs):
            """Ensure encrypted fields are not updated via 'update()'."""
            for name in kwargs:
                if any(
                    field.name == name for field in self.model.ENCRYPTED_FIELDS
                ):
                    raise ValidationError(
                        f"Cannot update encrypted field '{name}' via"
                        " 'update()'. Set the property on each instance"
                        " instead.",
                        code="cannot_update_encrypted_field",
                    )

            return super().update(**kwargs)

    objects: Manager[t.Self] = Manager()  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        abstract = True

    @property
    def dek_aead(self) -> "Aead":
        """Gets the AEAD primitive for this model's DEK."""
        raise NotImplementedError()
