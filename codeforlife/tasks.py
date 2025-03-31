"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import typing as t

from celery import schedules
from celery import shared_task as _shared_task
from django.conf import settings

from .types import Args, KwArgs


class CeleryBeat(t.Dict[str, t.Any]):
    """A Celery beat schedule.

    https://docs.celeryq.dev/en/v5.4.0/userguide/periodic-tasks.html
    """

    # Shorthand for convenience.
    crontab = schedules.crontab
    solar = schedules.solar

    def __init__(
        self,
        task: str,
        schedule: t.Union[int, schedules.crontab, schedules.solar],
        args: t.Optional[Args] = None,
        kwargs: t.Optional[KwArgs] = None,
    ):
        super().__init__()
        self["task"] = f"{settings.SERVICE_NAME}.{task}"
        self["schedule"] = schedule
        if args:
            self["args"] = args
        if kwargs:
            self["kwargs"] = kwargs


def shared_task(*args, **kwargs):
    """
    Wrapper around Celery's default shared_task decorator which namespaces all
    tasks to a specific service.
    """

    def get_name(func: t.Callable):
        return ".".join(
            [
                settings.SERVICE_NAME,
                func.__module__,
                func.__name__,
            ]
        )

    if len(args) == 1 and callable(args[0]):
        func = args[0]
        return _shared_task(name=get_name(func))(func)

    def wrapper(func: t.Callable):
        kwargs.pop("name", None)
        return _shared_task(name=get_name(func), *args, **kwargs)(func)

    return wrapper
