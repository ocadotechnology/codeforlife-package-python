"""
© Ocado Group
Created on 27/03/2025 at 16:52:42(+00:00).

Initializes our celery app.
"""

import logging
import subprocess
import typing as t

from celery import Celery

from ..tasks import get_task_name
from ..types import LogLevel
from .base import BaseServer


class CeleryServer(BaseServer, Celery):
    """A server for a Celery app."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        auto_run: bool = True,
        dump_request: bool = False,
        concurrency: t.Optional[int] = None,
        log_level: t.Optional[LogLevel] = "INFO",
        settings_module: str = "settings",
    ):
        # pylint: disable=line-too-long
        """Initialize a Celery app.

        Examples:
            ```
            from codeforlife.servers import CeleryServer

            celery_app = CeleryServer().app
            ```

        Args:
            auto_run: A flag designating whether to auto-run the server.
            dump_request: A flag designating whether to add the dump_request task (useful for debugging).
            concurrency: The concurrency of workers. None uses Celery's default.
            log_level: The log level. None uses Celery's default.
            settings_module: The dot-path to the settings module.
        """
        # pylint: enable=line-too-long

        super().__init__()

        self.app = self  # For readability: celery_app = `CeleryServer().app`.

        # Using a string here means the worker doesn't have to serialize
        # the configuration object to child processes.
        # - namespace='CELERY' means all celery-related configuration keys
        #   should have a `CELERY_` prefix.
        self.config_from_object(settings_module, namespace="CELERY")

        # Load task modules from all registered Django apps.
        self.autodiscover_tasks(["src"])

        if dump_request:

            @self.task(
                name=get_task_name("dump_request", settings_module),
                bind=True,
                ignore_result=True,
            )
            def _dump_request(self, *args, **kwargs):
                """Dumps its own request information."""

                logging.info("Request: %s", self.request)

        if auto_run and self.app_server_is_running:
            self.start_worker_as_subprocess(concurrency, log_level)

    def start_worker_as_subprocess(
        self,
        concurrency: t.Optional[int] = None,
        log_level: t.Optional[LogLevel] = "INFO",
    ):
        """
        Starts a worker using the 'celery worker' command.

        Args:
            concurrency: The concurrency of workers. None uses Celery's default.
            log_level: The log level. None uses Celery's default.
        """

        command = ["celery", f"--app={self.app_module}", "worker"]
        if log_level is not None:
            command.append(f"--loglevel={log_level}")
        if concurrency is not None:
            command.append(f"--concurrency={concurrency}")

        subprocess.run(command, check=True)
