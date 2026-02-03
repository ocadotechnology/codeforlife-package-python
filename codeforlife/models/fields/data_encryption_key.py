"""
© Ocado Group
Created on 19/01/2026 at 09:57:19(+00:00).

This field is responsible for managing the lifecycle of a DEK for a model
instance. When a new model instance is created, this field automatically
generates a new DEK, encrypts it with the KEK, and prepares it to be stored in
the database.

This is achieved using a `_Default` dataclass as a sentinel. In the
`DataEncryptionKeyField`'s `__init__` method, the `default` is set to the
`_Default` class. When a new model instance is created, Django sets the field's
value to an instance of `_Default()`.

The `_Default` dataclass has a field `dek` with a `default_factory` that points
to the `create_dek` function. This means that when `_Default` is instantiated, a
new DEK is automatically created.

The field's custom descriptor, `DataEncryptionKeyAttribute`, then intercepts the
`_Default` instance in its `__set__` method, extracts the newly created `dek`
from it, and sets it as the field's value on the model instance. This elegant
pattern ensures that a new DEK is generated only when a new model instance is
created.

The `contribute_to_class` method on `DataEncryptionKeyField` performs crucial
validations when the field is added to a model. It ensures that the model
inherits from the correct base class (`BaseDataEncryptionKeyModel`) and, most
importantly, it guarantees that a model can only have one
`DataEncryptionKeyField`. It does this by checking a class-level `_dek`
attribute; if this attribute is already set, it means another DEK field has
already been processed, and a `ValidationError` is raised. This prevents
developers from accidentally creating multiple encryption keys for a single
model instance, which would lead to ambiguity and potential data loss.
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
    """A default value holder that creates a new DEK on instantiation."""

    dek: bytes = field(default_factory=create_dek)


class DataEncryptionKeyAttribute(
    DeferredAttribute[
        AnyDataEncryptionKeyField, BaseDataEncryptionKeyModel, bytes
    ],
    t.Generic[AnyDataEncryptionKeyField],
):
    """
    Descriptor for DataEncryptionKeyField that handles the automatic creation of
    a new DEK and data shredding.
    """

    def __set__(
        self,
        instance,
        value: t.Optional[_Default],  # type: ignore[override]
    ):
        if isinstance(value, _Default):  # new instance is being created
            internal_value = value.dek
        elif value is None:  # data is being shredded
            internal_value = None
        else:
            raise ValidationError(
                "DataEncryptionKeyField can only be set to None.",
                code="cannot_set_value",
            )

        super().__set__(instance, internal_value)


class DataEncryptionKeyField(BinaryField):
    """
    A custom BinaryField to store an encrypted data encryption key (DEK).
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
        kwargs["editable"] = False  # DEK should not be editable in admin forms
        kwargs["default"] = _Default  # Default to a new DEK generator
        kwargs["null"] = True  # Allow null for data shredding
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

    @t.overload  # type: ignore[override]
    def __get__(  # Get the descriptor.
        self, instance: None, owner: t.Any
    ) -> DataEncryptionKeyAttribute[t.Self]: ...

    @t.overload
    def __get__(  # Get the value.
        self, instance: BaseDataEncryptionKeyModel, owner: t.Any
    ) -> t.Optional[bytes]: ...

    def __get__(  # Actual implementation of __get__.
        self, instance: t.Optional[BaseDataEncryptionKeyModel], owner: t.Any
    ):
        return t.cast(
            t.Union[DataEncryptionKeyAttribute[t.Self], t.Optional[bytes]],
            # pylint: disable-next=no-member
            super().__get__(instance, owner),
        )

    # Can only be set to None to allow data shredding.
    def __set__(self, instance: BaseDataEncryptionKeyModel, value: None): ...
