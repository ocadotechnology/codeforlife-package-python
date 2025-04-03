"""
© Ocado Group
Created on 01/04/2025 at 16:57:19(+01:00).
"""

import typing as t
from importlib import import_module

from celery import Celery, Task
from django.conf import settings

from ..tasks import CeleryBeatSchedule
from ..types import Args, KwArgs
from .test import TestCase


class CeleryTestCase(TestCase):
    """A test case for celery tasks."""

    # The dot-path of the module containing the Celery app.
    app_module: str = "application"
    # The name of the Celery app.
    app_name: str = "celery_app"
    # The Celery app instance. Auto-imported if not set.
    app: Celery

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "app"):
            cls.app = getattr(import_module(cls.app_module), cls.app_name)

    def apply_periodic_task(self, beat_name: str):
        """Apply a periodic task.

        Args:
            beat_name: The name of the beat in the schedule.
        """
        beat = t.cast(CeleryBeatSchedule, self.app.conf.beat_schedule)[
            beat_name
        ]

        task_dot_path = (
            beat["task"].removeprefix(f"{settings.SERVICE_NAME}.").split(".")
        )
        task_module = ".".join(task_dot_path[:-1])
        task_name = task_dot_path[-1]
        task: Task = getattr(import_module(task_module), task_name)

        args, kwargs = beat.get("args", tuple()), beat.get("kwargs", {})
        task.apply(*args, **kwargs)

    def apply_task(
        self,
        name: str,
        args: t.Optional[Args] = None,
        kwargs: t.Optional[KwArgs] = None,
    ):
        """Apply a task.

        Args:
            name: The name of the task.
            args: The args to pass to the task.
            kwargs: The keyword args to pass to the task.
        """
        task: Task = self.app.tasks[f"{settings.SERVICE_NAME}.{name}"]
        task.apply(*(args or tuple()), **(kwargs or {}))
