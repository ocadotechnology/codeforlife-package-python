"""
© Ocado Group
Created on 04/12/2023 at 14:36:56(+00:00).

Base models.
"""

import typing as t

from django.db import models
from django.utils.translation import gettext_lazy as _

from .fields import *


class AbstractModel(models.Model):
    """Base model to be inherited by other models throughout the CFL system."""

    id: int
    pk: int

    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    last_saved_at = models.DateTimeField(
        _("last saved at"),
        auto_now=True,
        help_text=_(
            "Record the last time the model was saved. This is used by our data"
            " warehouse to know what data was modified since the last scheduled"
            " data transfer from the database to the data warehouse."
        ),
    )

    delete_after = models.DateTimeField(
        _("delete after"),
        null=True,
        blank=True,
        help_text=_(
            "When this data is scheduled for deletion. Set to null if not"
            " scheduled for deletion. This is used by our data warehouse to"
            " transfer data that's been scheduled for deletion before it's"
            " actually deleted. Data will actually be deleted in a CRON job"
            " after this delete after."
        ),
    )

    class Meta:
        abstract = True


AnyModel = t.TypeVar("AnyModel", bound=AbstractModel)
