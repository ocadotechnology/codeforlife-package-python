"""Helpers for module "django.db.models.signals.post_save".
https://docs.djangoproject.com/en/3.2/ref/signals/#post-save
"""

from . import UpdateFields, _has_update_fields


def has_update_fields(actual: UpdateFields, expected: UpdateFields):
    """Check if the expected fields were updated.

    Args:
        actual: The fields that were updated.
        expected: A subset of the fields that were expected to be updated. If no
            fields were expected to be updated, set to None.

    Returns:
        If the fields that were expected to be updated are a subset of the
        fields that were updated.
    """

    return _has_update_fields(actual, expected)
