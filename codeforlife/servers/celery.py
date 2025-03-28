"""
© Ocado Group
Created on 27/03/2025 at 16:52:42(+00:00).

Initializes our celery app.
"""

import atexit
import os
import subprocess
import sys
import typing as t

import celery

from ..types import LogLevel

CELERY_MAIN_PATH = os.path.join(celery.__path__[0], "__main__.py")


class CeleryServer(celery.Celery):
    """A server for a Celery app."""

    def __init__(
        self,
        app: str = "application",
        debug: bool = bool(int(os.getenv("DEBUG", "1"))),
    ):
        """Initialize a Celery app.

        Examples:
            ```
            from codeforlife.servers import CeleryServer, DjangoServer

            # Make sure to set up Django before initializing!
            DjangoServer.setup()

            celery_app = CeleryServer().app
            ```

        Args:
            app: The dot-path to the Celery app.
            debug: A flag designating whether to run the app in debug mode.

        Raises:
            EnvironmentError: If "DJANGO_SETTINGS_MODULE" is not in os.environ.
        """

        if not "DJANGO_SETTINGS_MODULE" in os.environ:
            raise EnvironmentError(
                "Django's settings-module environment variable is required."
            )

        super().__init__()
        self.app = self
        self._app = app

        # Using a string here means the worker doesn't have to serialize
        # the configuration object to child processes.
        # - namespace='CELERY' means all celery-related configuration keys
        #   should have a `CELERY_` prefix.
        self.config_from_object("django.conf:settings", namespace="CELERY")

        # Load task modules from all registered Django apps.
        self.autodiscover_tasks()

        if debug:

            @self.task(name=f"{app}.debug", bind=True, ignore_result=True)
            def _debug(self, *args, **kwargs):
                """Dumps its own request information."""

                print(f"Request: {self.request!r}")

        if os.path.abspath(sys.argv[0]) != CELERY_MAIN_PATH:
            self.start_background_workers()
            self.start_background_beat()

    def start_background_workers(
        self,
        workers: t.Optional[t.Union[t.Set[str], t.Dict[str, int]]] = None,
        log_level: LogLevel = "INFO",
    ):
        # pylint: disable=line-too-long
        """
        Starts multiple Celery workers using the 'celery multi start' command.

        Args:
            workers: The names of the workers to start. A dict can be provided to set the concurrency per worker.
            log_level: The log level.
        """
        # pylint: enable=line-too-long

        commands: t.Dict[str, t.List[str]] = {}

        def build_command(worker: str, concurrency: int = 0):
            command = [
                "celery",
                "multi",
                "start",
                worker,
                f"--app={self._app}",
                f"--loglevel={log_level}",
            ]

            if concurrency > 0:
                command.append(f"--concurrency={concurrency}")

            commands[worker] = command

        workers = workers or {"w1"}

        if isinstance(workers, dict):
            for worker, concurrency in workers.items():
                build_command(worker, concurrency)
        else:
            for worker in workers:
                build_command(worker)

        successfully_started_workers: t.Set[str] = set()

        for worker, command in commands.items():
            try:
                subprocess.run(command, check=True)
                successfully_started_workers.add(worker)

            except Exception as ex:  # pylint: disable=broad-exception-caught
                print(f"Error starting Celery worker '{worker}': {ex}")

        if successfully_started_workers:
            atexit.register(
                self.stop_background_workers,
                successfully_started_workers,
                log_level,
            )

    def stop_background_workers(
        self,
        workers: t.Set[str],
        log_level: LogLevel = "INFO",
    ):
        """
        Stops multiple Celery workers using the 'celery multi stopwait' command.

        Args:
            workers: The names of the workers to stop.
            log_level: The log level.
        """

        try:
            subprocess.run(
                [
                    "celery",
                    "multi",
                    "stopwait",
                    *workers,
                    f"--app={self._app}",
                    f"--loglevel={log_level}",
                ],
                check=True,
            )

        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(f"Error stopping all Celery workers: {ex}")

    def start_background_beat(self, log_level: LogLevel = "INFO"):
        """Start Celery beat using the 'celery --app=app beat' command.

        Args:
            log_level: The log level.

        Returns:
            The background process running Celery beat.
        """

        try:
            process = subprocess.Popen(  # pylint: disable=consider-using-with
                [
                    "celery",
                    f"--app={self._app}",
                    "beat",
                    f"--loglevel={log_level}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            atexit.register(process.terminate)

            return process

        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(f"Error starting Celery beat: {ex}")

        return None
