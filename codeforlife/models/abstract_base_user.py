"""
© Ocado Group
Created on 06/11/2024 at 16:38:15(+00:00).
"""

import typing as t

from django.contrib.auth.models import AbstractBaseUser as _AbstractBaseUser
from django.utils.translation import gettext_lazy as _

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta

    from .abstract_base_session import AbstractBaseSession
else:
    TypedModelMeta = object


class AbstractBaseUser(_AbstractBaseUser):
    """
    Base user class to be inherited by all user classes.
    https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    """

    id: int
    pk: int
    session: "AbstractBaseSession"

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta(TypedModelMeta):
        abstract = True
        verbose_name = _("user")
        verbose_name_plural = _("users")
