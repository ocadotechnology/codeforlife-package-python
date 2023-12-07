"""
© Ocado Group
Created on 04/12/2023 at 14:36:56(+00:00).

Base models.
"""

import typing as t
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from .fields import *


class AbstractModel(models.Model):
    """Base model to be inherited by other models throughout the CFL system."""

    class QuerySet(models.QuerySet):
        """Custom queryset to support CFL's system's operations."""

        model: "AbstractModel"  # type: ignore[assignment]

        def update(self, **kwargs):
            """Updates all models in the queryset and notes when they were last
            saved.

            Args:
                last_saved_at: When these models were last modified.

            Returns:
                The number of models updated.
            """

            kwargs["last_saved_at"] = timezone.now()
            return super().update(**kwargs)

        def delete(self, wait: t.Optional[timedelta] = None):
            """Schedules all models in the queryset for deletion.

            Args:
                wait: How long to wait before these model are deleted. If not
                    set, the class-level default value is used.
            """

            wait = wait or self.model.delete_wait
            self.update(delete_after=timezone.now() + wait)

    objects = models.Manager.from_queryset(QuerySet)()

    # Type hints for Django's runtime-generated fields.
    id: int
    pk: int

    # Default for how long to wait before a model is deleted.
    delete_wait = timedelta(days=3)

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
            " after this point in time."
        ),
    )

    # pylint: disable-next=missing-class-docstring
    class Meta(TypedModelMeta):
        abstract = True

    # pylint: disable-next=arguments-differ
    def delete(  # type: ignore[override]
        self,
        wait: t.Optional[timedelta] = None,
    ):
        """Schedules the deletion of this model.

        Args:
            wait: How long to wait before this model is deleted. If not set, the
                class-level default value is used.
        """

        wait = wait or self.delete_wait
        self.delete_after = timezone.now() + wait
        self.save()


AnyModel = t.TypeVar("AnyModel", bound=AbstractModel)
