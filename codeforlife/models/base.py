"""
© Ocado Group
Created on 19/01/2024 at 15:18:48(+00:00).

Base model for all Django models.
"""

import typing as t

from django.db.models import Manager
from django.db.models import Model as _Model

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class Model(_Model):
    """Base for all models."""

    objects: Manager[t.Self]

    class Meta(TypedModelMeta):
        abstract = True


AnyModel = t.TypeVar("AnyModel", bound=Model)
