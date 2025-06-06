"""
© Ocado Group
Created on 01/04/2025 at 16:57:19(+01:00).
"""

import typing as t
from importlib import import_module

from celery import Celery, Task

from ..tasks import get_task_name
from ..types import Args, KwArgs
from .test import TestCase


class CeleryTestCase(TestCase):
    """A test case for celery tasks."""

    # The dot-path of the module containing the Celery app.
    app_module: str = "application"
    # The name of the Celery app.
    app_name: str = "celery"
    # The Celery app instance. Auto-imported if not set.
    app: Celery

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "app"):
            cls.app = getattr(import_module(cls.app_module), cls.app_name)

        return super().setUpClass()

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
        task: Task = self.app.tasks[get_task_name(name)]
        task.apply(args=args, kwargs=kwargs)
