"""
© Ocado Group
Created on 19/01/2024 at 15:18:48(+00:00).

Base model for all Django models.
"""

import typing as t

from django.db.models import Model as _Model
from django_stubs_ext.db.models import TypedModelMeta

Id = t.TypeVar("Id")


class Model(_Model, t.Generic[Id]):
    """A base class for all Django models."""

    id: Id
    pk: Id

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta(TypedModelMeta):
        abstract = True


AnyModel = t.TypeVar("AnyModel", bound=Model)
