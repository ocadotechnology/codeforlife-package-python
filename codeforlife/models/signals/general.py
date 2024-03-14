"""
© Ocado Group
Created on 14/03/2024 at 12:51:50(+00:00).
"""

import typing as t

from django.db.models import Model

AnyModel = t.TypeVar("AnyModel", bound=Model)
UpdateFields = t.Optional[t.FrozenSet[str]]


def update_fields_includes(update_fields: UpdateFields, includes: t.Set[str]):
    """Check the call to .save() includes the update-fields specified.

    Args:
        update_fields: The update-fields provided in the call to .save().
        includes: The fields that should be included in the update-fields.

    Returns:
        The fields missing in the update-fields. If update-fields is None, None
        is returned.
    """

    if update_fields is None:
        return None

    return includes.difference(update_fields)


def assert_update_fields_includes(
    update_fields: UpdateFields, includes: t.Set[str]
):
    """Assert the call to .save() includes the update-fields specified.

    Args:
        update_fields: The update-fields provided in the call to .save().
        includes: The fields that should be included in the update-fields.
    """
    missing_update_fields = update_fields_includes(update_fields, includes)
    if missing_update_fields is not None:
        assert not missing_update_fields, (
            "Call to .save() did not include the following update-fields: "
            f"{', '.join(missing_update_fields)}."
        )
