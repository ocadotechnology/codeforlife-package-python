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
from .deferred_attribute import DeferredAttribute

if t.TYPE_CHECKING:
    from ...models import DataEncryptionKeyModel

AnyDataEncryptionKeyField = t.TypeVar(
    "AnyDataEncryptionKeyField", bound="DataEncryptionKeyField"
)


@dataclass(frozen=True)
class _Default:
    """A default value holder for DataEncryptionKeyField."""

    dek: bytes = field(default_factory=create_dek)


class DataEncryptionKeyAttribute(
    DeferredAttribute[
        AnyDataEncryptionKeyField, "DataEncryptionKeyModel", bytes
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

    model: t.Type["DataEncryptionKeyModel"]

    descriptor_class = DataEncryptionKeyAttribute

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
        self, instance: "DataEncryptionKeyModel", owner: t.Any
    ) -> t.Optional[bytes]: ...

    # Actual implementation of __get__.
    def __get__(
        self, instance: t.Optional["DataEncryptionKeyModel"], owner: t.Any
    ):
        return t.cast(
            t.Union[DataEncryptionKeyAttribute[t.Self], t.Optional[bytes]],
            # pylint: disable-next=no-member
            super().__get__(instance, owner),
        )

    # Can only be set to None to allow data shredding.
    def __set__(self, instance: "DataEncryptionKeyModel", value: None): ...
