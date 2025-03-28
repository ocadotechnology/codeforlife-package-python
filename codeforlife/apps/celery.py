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

    def start_background_beat(self, log_level: LogLevel = "INFO"):
        """Start Celery beat using the 'celery --app=app beat' command.

        Args:
            log_level: The log level.

        Returns:
            The background process running Celery beat.
        """

        print("Starting Celery beat.")

        try:
            process = subprocess.Popen(  # pylint: disable=consider-using-with
                [
                    "celery",
                    f"--app={self.app}",
                    "beat",
                    f"--loglevel={log_level}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("Successfully started Celery beat.")

            atexit.register(self.stop_background_beat, process)

            return process

        except subprocess.CalledProcessError as error:
            print(f"Error starting Celery beat: {error}")

        return None

    def stop_background_beat(self, process: subprocess.Popen):
        """Stop a Celery beat process.

        Args:
            process: The process to stop.
        """

        print("Stopping Celery beat.")

        try:
            process.terminate()
            print("Successfully stopped Celery beat.")

        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(f"Error stopping Celery beat: {ex}")

    def handle_startup(self):
        """Handle the startup procedure of a Celery app.

        Examples:
            ```
            from codeforlife.apps import CeleryApplication, DjangoApplication

            # Make sure to set up Django before starting!
            DjangoApplication.setup()

            celery_app = CeleryApplication().handle_startup()
            ```

        Returns:
            The Celery app instance for convenience.
        """

        self.start_background_workers()
        self.start_background_beat()

        return self
