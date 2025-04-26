"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import typing as t
from importlib import import_module
from types import ModuleType

from celery import shared_task as _shared_task


def get_task_name(
    task: t.Union[str, t.Callable],
    settings_module: t.Union[str, ModuleType] = "settings",
):
    """Namespace a task by the service it's in.

    Args:
        task: The name of the task.
        settings_module: The settings module or the dot-path to it.

    Returns:
        The name of the task in the format: "{SERVICE_NAME}.{TASK_NAME}".
    """

    if isinstance(settings_module, str):
        settings_module = import_module(settings_module)

    if callable(task):
        task = f"{task.__module__}.{task.__name__}"

    return f"{settings_module.SERVICE_NAME}.{task}"


def shared_task(*args, **kwargs):
    """
    Wrapper around Celery's default shared_task decorator which namespaces all
    tasks to a specific service.
    """

    if len(args) == 1 and callable(args[0]):
        task = args[0]
        return _shared_task(name=get_task_name(task))(task)

    def wrapper(task: t.Callable):
        task = kwargs.pop("name", task)
        return _shared_task(name=get_task_name(task), *args, **kwargs)(task)

    return wrapper


def get_local_sqs_url(aws_region: str, service_name: str):
    """Get the URL of an SQS queue in the local environment.

    Args:
        aws_region: The AWS region.
        service_name: The service this SQS queue belongs to.

    Returns:
        The SQS queue's URL.
    """
    return (
        f"http://sqs.{aws_region}.localhost.localstack.cloud:4566"
        f"/000000000000/{service_name}"
    )
