"""
© Ocado Group
Created on 27/03/2025 at 16:52:42(+00:00).

Initializes our celery app.
"""

import atexit
import os
import subprocess
import typing as t

from celery import Celery as _Celery

from ..types import LogLevel


class CeleryApplication(_Celery):
    """A server for a Celery app."""

    def __init__(
        self,
        app: str = "application",
        debug: bool = bool(int(os.getenv("DEBUG", "1"))),
    ):
        """Initialize a Celery app.

        Args:
            app: The Celery app name.
            debug: A flag designating whether to run the app in debug mode.

        Raises:
            EnvironmentError: If "DJANGO_SETTINGS_MODULE" is not in os.environ.
        """

        if not "DJANGO_SETTINGS_MODULE" in os.environ:
            raise EnvironmentError(
                "Django's settings-module environment variable is required."
            )

        super().__init__()

        self.app = app

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

        print("Starting all Celery workers.")

        commands: t.Dict[str, t.List[str]] = {}

        def build_command(worker: str, concurrency: int = 0):
            command = [
                "celery",
                "multi",
                "start",
                worker,
                f"--app={self.app}",
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
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"Successfully started Celery worker '{worker}'.")
                print(process.stdout)

                successfully_started_workers.add(worker)

            except subprocess.CalledProcessError as e:
                print(f"Error starting Celery worker '{worker}': {e}")
                print(e.stderr)

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

        print("Stopping all Celery workers.")

        try:
            process = subprocess.run(
                [
                    "celery",
                    "multi",
                    "stopwait",
                    *workers,
                    f"--app={self.app}",
                    f"--loglevel={log_level}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print("Successfully stopped all Celery workers.")
            print(process.stdout)

        except subprocess.CalledProcessError as error:
            print(f"Error stopping all Celery workers: {error}")
            print(error.stderr)

    @classmethod
    def handle_startup(cls, name: str):
        """Handle the startup procedure of a Celery app.

        Examples:
            ```
            import os
            from codeforlife.apps import CeleryApplication

            # Make sure to set this before starting the Celery app!
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

            celery_app = CeleryApplication.handle_startup(__name__)
            ```

        Args:
            name: The name of the file calling this function.

        Returns:
            An instance of a Celery app.
        """

        app = cls()

        if name == "__main__":
            app.start_background_workers()

        return app
