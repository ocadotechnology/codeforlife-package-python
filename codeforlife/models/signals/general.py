"""
© Ocado Group
Created on 14/03/2024 at 12:51:50(+00:00).
"""

import typing as t

from django.core.exceptions import ValidationError
from django.db.models import Model

AnyModel = t.TypeVar("AnyModel", bound=Model)
UpdateFields = t.Optional[t.FrozenSet[str]]


def update_fields_includes(
    update_fields: UpdateFields, includes: t.Union[t.Set[str], t.FrozenSet[str]]
):
    """Check the call to .save() includes the update-fields specified.

    Args:
        update_fields: The update-fields provided in the call to .save().
        includes: The fields that should be included in the update-fields.

    Returns:
        A flag designating if the fields are included in the update-fields.
    """
    return (
        update_fields is not None
        and len(update_fields) > 0
        and includes.issubset(update_fields)
    )


def validate_update_fields_includes_none_or_all(
    update_fields: UpdateFields, includes: t.Union[t.Set[str], t.FrozenSet[str]]
):
    """
    Validates that either none or all of the fields are included in the
    update-fields.

    Args:
        update_fields: The update-fields provided in the call to .save().
        includes: The fields that should be included in the update-fields.

    Raises:
        ValidationError: If some but not all of the fields are included.
    """
    if (
        update_fields
        and update_fields.intersection(includes)
        and not update_fields.issuperset(includes)
    ):
        raise ValidationError(
            "Either none or all of the following fields must be included in "
            f"update_fields: {', '.join(includes)}",
            code="update_fields_incomplete",
        )
