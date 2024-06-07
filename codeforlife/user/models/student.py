# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 14/02/2024 at 17:16:44(+00:00).
"""

import typing as t

from common.models import Student, StudentModelManager
from django.db import models

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


# TODO: This model is legacy and should be removed in the new data schema.
class Independent(Student):
    """An independent student."""

    class_field: None

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(StudentModelManager):
        # pylint: disable-next=missing-function-docstring
        def get_queryset(self):
            return super().get_queryset().filter(class_field__isnull=True)

    objects: models.Manager["Independent"] = Manager()
