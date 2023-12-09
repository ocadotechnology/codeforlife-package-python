"""
© Ocado Group
Created on 04/12/2023 at 14:36:56(+00:00).

Base models. Tests at: codeforlife.user.tests.models.test_abstract
"""

import typing as t
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from .fields import *


class Model(models.Model):
    """Provide type hints for general model attributes."""

    id: int
    pk: int
    objects: models.Manager
    DoesNotExist: t.Type[ObjectDoesNotExist]

    class Meta(TypedModelMeta):
        abstract = True


AnyModel = t.TypeVar("AnyModel", bound=Model)


class WarehouseModel(Model):
    """To be inherited by all models whose data is to be warehoused."""

    class QuerySet(models.QuerySet):
        """Custom queryset to support CFL's system's operations."""

        model: "WarehouseModel"  # type: ignore[assignment]

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
                    set, the class-level default value is used. To delete
                    immediately, set wait to 0 with timedelta().
            """

            if wait is None:
                wait = self.model.delete_wait

            if wait == timedelta():
                super().delete()
            else:
                self.update(delete_after=timezone.now() + wait)

    class Manager(models.Manager[AnyModel], t.Generic[AnyModel]):
        """Custom Manager for all warehouse model managers to inherit."""

        def get_queryset(self):
            """Get custom query set.

            Returns:
                A warehouse query set.
            """

            return WarehouseModel.QuerySet(
                model=self.model,
                using=self._db,
                hints=self._hints,  # type: ignore[attr-defined]
            )

        def filter(self, *args, **kwargs):
            """A stub that return our custom queryset."""

            return t.cast(
                WarehouseModel.QuerySet,
                super().filter(*args, **kwargs),
            )

        def exclude(self, *args, **kwargs):
            """A stub that return our custom queryset."""

            return t.cast(
                WarehouseModel.QuerySet,
                super().exclude(*args, **kwargs),
            )

        def all(self):
            """A stub that return our custom queryset."""

            return t.cast(
                WarehouseModel.QuerySet,
                super().all(),
            )

    objects: Manager = Manager()

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

    class Meta(TypedModelMeta):
        abstract = True

    # pylint: disable-next=arguments-differ
    def delete(  # type: ignore[override]
        self,
        *args,
        wait: t.Optional[timedelta] = None,
        **kwargs,
    ):
        """Schedules the deletion of this model.

        Args:
            wait: How long to wait before this model is deleted. If not set, the
                class-level default value is used. To delete immediately, set
                wait to 0 with timedelta().
        """

        if wait is None:
            wait = self.delete_wait

        if wait == timedelta():
            super().delete(*args, **kwargs)
        else:
            self.delete_after = timezone.now() + wait
            self.save(*args, **kwargs)


AnyWarehouseModel = t.TypeVar("AnyWarehouseModel", bound=WarehouseModel)
