"""Helpers for module "django.db.models.signals".
https://docs.djangoproject.com/en/3.2/ref/signals/#module-django.db.models.signals
"""

import typing as t

UpdateFields = t.Optional[t.FrozenSet[str]]


def _has_update_fields(actual: UpdateFields, expected: UpdateFields):
    if expected is None:
        return actual is None
    if actual is None:
        return False

    return all(update_field in actual for update_field in expected)
