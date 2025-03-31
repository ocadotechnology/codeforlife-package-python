"""
© Ocado Group
Created on 27/03/2025 at 16:52:42(+00:00).

Initializes our celery app.
"""

import atexit
import logging
import subprocess
import typing as t

from celery import Celery
from django.core.management import call_command as call_django_command

from ..types import LogLevel
from .base import BaseServer


class CeleryServer(BaseServer, Celery):
    """A server for a Celery app."""

    def __init__(self, auto_run: bool = True, dump_request: bool = False):
        # pylint: disable=line-too-long
        """Initialize a Celery app.

        Examples:
            ```
            from codeforlife.servers import CeleryServer, DjangoServer

            # Make sure to set up Django before initializing!
            DjangoServer.setup()

            celery_app = CeleryServer().app
            ```

        Args:
            auto_run: A flag designating whether to auto-run the server.
            dump_request: A flag designating whether to add the dump_request task (useful for debugging).

        Raises:
            EnvironmentError: If "DJANGO_SETTINGS_MODULE" is not in os.environ.
        """
        # pylint: enable=line-too-long

        call_django_command("check")

        # pylint: disable-next=import-outside-toplevel
        from django.conf import settings

        super().__init__()

        self.app = self  # For readability: celery_app = `CeleryServer().app`.

        # Using a string here means the worker doesn't have to serialize
        # the configuration object to child processes.
        # - namespace='CELERY' means all celery-related configuration keys
        #   should have a `CELERY_` prefix.
        self.config_from_object(settings, namespace="CELERY")

        # Load task modules from all registered Django apps.
        self.autodiscover_tasks()

        if dump_request:

            @self.task(
                name=f"{settings.SERVICE_NAME}.dump_request",
                bind=True,
                ignore_result=True,
            )
            def _dump_request(self, *args, **kwargs):
                """Dumps its own request information."""

                logging.info("Request: %s", self.request)

        if auto_run and (
            self.app_server_is_running() or self.django_dev_server_is_running()
        ):
            self.start_workers_as_subprocesses()
            self.start_heartbeat_as_subprocess()

    def start_workers_as_subprocesses(
        self,
        workers: t.Optional[t.Union[t.Set[str], t.Dict[str, int]]] = None,
        log_level: t.Optional[LogLevel] = "INFO",
    ):
        # pylint: disable=line-too-long
        """
        Starts multiple workers using the 'celery worker' command.

        Args:
            workers: The names of the workers to start. A dict can be provided to set the concurrency per worker.
            log_level: The log level. None will silence all logs.

        Returns:
            The subprocesses running the workers.
        """
        # pylint: enable=line-too-long

        workers = workers or {"w1"}
        if isinstance(workers, set):
            workers = {worker: 0 for worker in workers}

        processes: t.Dict[str, subprocess.Popen[bytes]] = {}
        for worker, concurrency in workers.items():
            command = ["celery", f"--app={self.app_module}", "worker"]
            if log_level:
                command.append(f"--loglevel={log_level}")

                stdout, stderr = (None, None)  # Use defaults.
            else:
                stdout, stderr = (subprocess.DEVNULL, subprocess.DEVNULL)
            if concurrency > 0:
                command.append(f"--concurrency={concurrency}")

            try:
                # pylint: disable-next=consider-using-with
                process = subprocess.Popen(
                    command, stdout=stdout, stderr=stderr
                )

                atexit.register(process.terminate)

                processes[worker] = process

            except Exception as ex:  # pylint: disable=broad-exception-caught
                print(f"Error starting Celery worker '{worker}': {ex}")

        return processes

    def start_heartbeat_as_subprocess(
        self, log_level: t.Optional[LogLevel] = "INFO"
    ):
        """Start heartbeat using the 'celery beat' command.

        Args:
            log_level: The log level. None will silence all logs.

        Returns:
            The subprocess running the heartbeat.
        """

        command = ["celery", f"--app={self.app_module}", "beat"]
        if log_level:
            command.append(f"--loglevel={log_level}")

            stdout, stderr = (None, None)  # Use defaults.
        else:
            stdout, stderr = (subprocess.DEVNULL, subprocess.DEVNULL)

        try:
            process = subprocess.Popen(  # pylint: disable=consider-using-with
                command, stdout=stdout, stderr=stderr
            )

            atexit.register(process.terminate)

            return process

        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(f"Error starting Celery beat: {ex}")

        return None
