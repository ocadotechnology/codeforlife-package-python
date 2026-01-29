"""
© Ocado Group
Created on 19/01/2026 at 09:57:19(+00:00).
"""

import typing as t
from dataclasses import dataclass, field

from django.core.exceptions import ValidationError
from django.db.models import BinaryField
from django.utils.translation import gettext_lazy as _

from ...encryption import create_dek
from ...types import KwArgs
from ..base_data_encryption_key import BaseDataEncryptionKeyModel
from .deferred_attribute import DeferredAttribute

AnyDataEncryptionKeyField = t.TypeVar(
    "AnyDataEncryptionKeyField", bound="DataEncryptionKeyField"
)


@dataclass(frozen=True)
class _Default:
    """A default value holder for DataEncryptionKeyField."""

    dek: bytes = field(default_factory=create_dek)


class DataEncryptionKeyAttribute(
    DeferredAttribute[
        AnyDataEncryptionKeyField, BaseDataEncryptionKeyModel, bytes
    ],
    t.Generic[AnyDataEncryptionKeyField],
):
    """Descriptor for DataEncryptionKeyField."""

    def __set__(
        self,
        instance,
        value: t.Optional[_Default],  # type: ignore[override]
    ):
        if isinstance(value, _Default):
            internal_value = value.dek
        elif value is None:
            internal_value = None
        else:
            raise ValidationError(
                "DataEncryptionKeyField can only be set to None.",
                code="cannot_set_value",
            )

        super().__set__(instance, internal_value)


class DataEncryptionKeyField(BinaryField):
    """
    A custom BinaryField to store a encrypted data encryption key (DEK).
    """

    model: t.Type[BaseDataEncryptionKeyModel]

    descriptor_class = DataEncryptionKeyAttribute

    # --------------------------------------------------------------------------
    # Construction & Deconstruction
    # --------------------------------------------------------------------------

    default_verbose_name = "data encryption key"
    default_help_text = (
        "The encrypted data encryption key (DEK) for this model."
    )

    def set_init_kwargs(self, kwargs: KwArgs):
        """Sets common init kwargs."""
        kwargs["editable"] = False
        kwargs["default"] = _Default
        kwargs["null"] = True
        kwargs.setdefault("verbose_name", _(self.default_verbose_name))
        kwargs.setdefault("help_text", _(self.default_help_text))

    def __init__(self, **kwargs):
        if kwargs.get("editable", False):
            raise ValidationError(
                "DataEncryptionKeyField cannot be editable.",
                code="editable_not_allowed",
            )
        if "default" in kwargs:
            raise ValidationError(
                "DataEncryptionKeyField cannot have a default value.",
                code="default_not_allowed",
            )
        if not kwargs.get("null", True):
            raise ValidationError(
                "DataEncryptionKeyField must allow null to support data"
                " shredding.",
                code="null_not_allowed",
            )

        self.set_init_kwargs(kwargs)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        self.set_init_kwargs(kwargs)
        return name, path, args, kwargs

    # --------------------------------------------------------------------------
    # Django Model Field Integration
    # --------------------------------------------------------------------------

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # Skip fake models used for migrations.
        if cls.__module__ == "__fake__":
            return

        # Ensure the model subclasses BaseDataEncryptionKeyModel.
        if not issubclass(cls, BaseDataEncryptionKeyModel):
            raise ValidationError(
                f"'{cls.__module__}.{cls.__name__}' must subclass"
                f" '{BaseDataEncryptionKeyModel.__module__}."
                f"{BaseDataEncryptionKeyModel.__name__}'.",
                code="invalid_model_base_class",
            )

        # Ensure only one DEK field per model.
        # pylint: disable-next=protected-access
        if cls._dek is not None:
            raise ValidationError(
                f"'{cls.__module__}.{cls.__name__}' already has a"
                " DataEncryptionKeyField defined.",
                code="multiple_dek_fields_not_allowed",
            )

        # Set the class DEK field reference.
        # pylint: disable-next=protected-access
        cls._dek = getattr(cls, self.name)

    # --------------------------------------------------------------------------
    # Descriptor Methods
    # --------------------------------------------------------------------------

    # Get the descriptor.
    @t.overload  # type: ignore[override]
    def __get__(
        self, instance: None, owner: t.Any
    ) -> DataEncryptionKeyAttribute[t.Self]: ...

    # Get the value.
    @t.overload
    def __get__(
        self, instance: BaseDataEncryptionKeyModel, owner: t.Any
    ) -> t.Optional[bytes]: ...

    # Actual implementation of __get__.
    def __get__(
        self, instance: t.Optional[BaseDataEncryptionKeyModel], owner: t.Any
    ):
        return t.cast(
            t.Union[DataEncryptionKeyAttribute[t.Self], t.Optional[bytes]],
            # pylint: disable-next=no-member
            super().__get__(instance, owner),
        )

    # Can only be set to None to allow data shredding.
    def __set__(self, instance: BaseDataEncryptionKeyModel, value: None): ...
