"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import typing as t

from celery import shared_task as _shared_task
from celery.schedules import crontab, solar
from django.conf import settings

from .types import Args, KwArgs

Schedule = t.Union[int, crontab, solar]


class CeleryBeat(t.TypedDict):
    """A Celery beat schedule.

    https://docs.celeryq.dev/en/v5.4.0/userguide/periodic-tasks.html
    """

    task: str
    schedule: Schedule
    args: t.NotRequired[Args]
    kwargs: t.NotRequired[KwArgs]


class CeleryBeatSchedule(t.Dict[str, CeleryBeat]):
    """A celery beat schedule.

    https://docs.celeryq.dev/en/v5.4.0/userguide/periodic-tasks.html
    """

    def __init__(
        self,
        namespace_tasks: bool = True,
        **beat_schedule: CeleryBeat,
    ):
        """Initialize a beat schedule.

        Args:
            namespace_tasks: A flag designating whether to namespace beat tasks.
        """

        if namespace_tasks:
            for beat in beat_schedule.values():
                beat["task"] = namespace_task(beat["task"])

        super().__init__(beat_schedule)


def namespace_task(task: t.Union[str, t.Callable]):
    """Namespace a task by the service it's in.

    Args:
        task: The name of the task.

    Returns:
        The name of the task in the format: "{SERVICE_NAME}.{TASK_NAME}".
    """

    if callable(task):
        task = f"{task.__module__}.{task.__name__}"

    return f"{settings.SERVICE_NAME}.{task}"


def shared_task(*args, **kwargs):
    """
    Wrapper around Celery's default shared_task decorator which namespaces all
    tasks to a specific service.
    """

    if len(args) == 1 and callable(args[0]):
        func = args[0]
        return _shared_task(name=namespace_task(func))(func)

    def wrapper(func: t.Callable):
        kwargs.pop("name", None)
        return _shared_task(name=namespace_task(func), *args, **kwargs)(func)

    return wrapper
