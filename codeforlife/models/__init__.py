import typing as t

from django.db.models import Model as _Model


class Model(_Model):
    """A base class for all Django models.

    Args:
        _Model (django.db.models.Model): Django's model class.
    """

    id: int
    pk: int


AnyModel = t.TypeVar("AnyModel", bound=Model)
