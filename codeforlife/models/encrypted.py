import typing as t

from django.apps import apps
from django.core import checks
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

    # pylint: disable-next=too-few-public-methods
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

    @classmethod
    def _check_associated_data(cls, **kwargs):
        """
        Check 'associated_data' values are unique across all EncryptedModel
        subclasses.
        """
        errors: t.List[checks.Error] = []

        if cls._meta.abstract:
            return errors

        # Ensure associated_data is defined.
        if not hasattr(cls, "associated_data"):
            errors.append(
                checks.Error(
                    "Must define an associated_data attribute.",
                    hint=f"{cls.__module__}.{cls.__name__}",
                    obj=cls,
                    id="codeforlife.user.E001",
                )
            )
        # Ensure associated_data is a string.
        elif not isinstance(cls.associated_data, str):
            errors.append(
                checks.Error(
                    "associated_data must be a string.",
                    hint=f"{cls.__module__}.{cls.__name__}",
                    obj=cls,
                    id="codeforlife.user.E002",
                )
            )
        # Ensure associated_data is not empty.
        elif not cls.associated_data:
            errors.append(
                checks.Error(
                    "associated_data cannot be empty.",
                    hint=f"{cls.__module__}.{cls.__name__}",
                    obj=cls,
                    id="codeforlife.user.E003",
                )
            )
        # Ensure associated_data is unique.
        else:
            for model in apps.get_models():
                if (
                    not model is cls
                    and not model._meta.abstract
                    and issubclass(model, EncryptedModel)
                    and model.associated_data == cls.associated_data
                ):
                    errors.append(
                        checks.Error(
                            "Duplicate 'associated_data' detected:"
                            f" '{cls.associated_data}'",
                            hint=(
                                f"{cls.__module__}.{cls.__name__}"
                                " shares this ID with"
                                f" {model.__module__}.{model.__name__}."
                            ),
                            obj=cls,
                            id="codeforlife.user.E004",
                        )
                    )

        return errors

    @classmethod
    def check(cls, **kwargs):
        """Run model checks, including custom checks for encrypted models."""
        errors = super().check(**kwargs)
        errors.extend(cls._check_associated_data(**kwargs))
        return errors

    @property
    def dek_aead(self) -> "Aead":
        """Gets the AEAD primitive for this model's DEK."""
        raise NotImplementedError()
