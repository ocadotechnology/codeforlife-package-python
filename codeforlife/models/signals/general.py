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
        A flag designating if the fields are included in the update-fields.
    """
    return update_fields and includes.issubset(update_fields)
