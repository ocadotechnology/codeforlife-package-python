"""
© Ocado Group
Created on 05/06/2025 at 17:33:56(+01:00).
"""

import atexit
import logging
import multiprocessing
import os
import subprocess
import sys
import typing as t
from functools import cached_property
from importlib import import_module

from celery import Celery
from django import setup as setup_django
from django.core.asgi import get_asgi_application as get_django_asgi_app
from django.core.management import call_command as call_django_command
from django.core.wsgi import get_wsgi_application as get_django_wsgi_app
from gunicorn.app.base import BaseApplication  # type: ignore[import-untyped]

from .tasks import get_task_name
from .types import DatabaseEngine, Env, LogLevel


# pylint: disable-next=abstract-method,too-many-instance-attributes
class Server(BaseApplication):
    """Serves a service in different modes."""

    Mode = t.Literal["django", "celery"]

    # The entrypoint module.
    main_module = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    # The dot-path of the application module.
    app_module: str = "application"
    # The dot-path of the settings module.
    settings_module: str = "settings"
    # The dot-path of Django's manage module.
    django_manage_module: str = "manage"
    # The dot-path of the source-code module.
    src_module: str = "src"
    # The port the app is served on.
    app_port: int = 8080

    @cached_property
    def app_server_is_running(self):
        """Whether or not the app server is running."""
        return self.main_module == self.app_module

    @cached_property
    def django_dev_server_is_running(self):
        """Whether or not the Django development server is running."""
        return (
            self.main_module == self.django_manage_module
            and sys.argv[1] == "runserver"
        )

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        mode: Mode = t.cast(Mode, os.getenv("SERVER_MODE", "django")),
        workers: int = int(os.getenv("SERVER_WORKERS", "0")),
        log_level: t.Optional[LogLevel] = t.cast(
            LogLevel, os.getenv("LOG_LEVEL", "INFO")
        ),
        db_engine: DatabaseEngine = "postgresql",
        dump_request: bool = False,
    ):
        # pylint: disable=line-too-long
        """Initialize a service's app-server.

        Examples:
            ```
            from codeforlife.server import Server

            Server().run()
            ```

        Args:
            mode: The mode to run in. Note, "celery" will start Django with only the health-check url.
            workers: The number of workers. 0 will auto-calculate. Note, "celery" will create 1 Django worker.
            log_level: The log level. None uses the default.
            db_engine: The database's engine type.
            dump_request: A flag designating whether to add the dump_request Celery task (useful for debugging).
        """
        # pylint: enable=line-too-long

        if mode != "django" and self.django_dev_server_is_running:
            mode = "django"
        os.environ["SERVER_MODE"] = mode
        self.mode = mode

        if log_level:
            os.environ["LOG_LEVEL"] = log_level
        self.log_level = log_level

        os.environ["DB_ENGINE"] = db_engine
        self.db_engine = db_engine

        if mode == "django":
            # https://docs.gunicorn.org/en/stable/design.html#how-many-workers
            workers = workers or (multiprocessing.cpu_count() * 2) + 1
        self.workers = workers

        if self.app_server_is_running:
            os.environ["SERVICE_PORT"] = str(self.app_port)

        os.environ["DJANGO_SETTINGS_MODULE"] = self.settings_module
        setup_django()

        self.django_asgi_app = get_django_asgi_app()
        self.django_wsgi_app = get_django_wsgi_app()
        self.celery_app = Celery()

        self.options = {
            "bind": f"0.0.0.0:{self.app_port}",
            "workers": 1 if mode == "celery" else workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "forwarded_allow_ips": "*",
        }

        if mode == "celery":
            # Using a string here means the worker doesn't have to serialize
            # the configuration object to child processes.
            # - namespace='CELERY' means all celery-related configuration keys
            #   should have a `CELERY_` prefix.
            self.celery_app.config_from_object(
                "django.conf:settings", namespace="CELERY"
            )

            # Load task modules from all registered Django apps.
            self.celery_app.autodiscover_tasks([self.src_module])

            if dump_request:

                @self.celery_app.task(
                    name=get_task_name("dump_request"),
                    bind=True,
                    ignore_result=True,
                )
                def _dump_request(self, *args, **kwargs):
                    """Dumps its own request information."""

                    logging.info("Request: %s", self.request)

        super().__init__()

        # Set the apps as global variables in the app module.
        app = import_module(self.app_module)
        app.django_wsgi = self.django_wsgi_app  # type: ignore[attr-defined]
        app.celery = self.celery_app  # type: ignore[attr-defined]

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.django_asgi_app

    # pylint: disable-next=dangerous-default-value
    def run(
        self,
        migrate: bool = True,
        collect_static: bool = True,
        create_sites: bool = True,
        load_fixtures: t.Optional[t.Set[str]] = {src_module},
    ):
        """Run the server in the set mode.

        Args:
            migrate: A flag designating whether to migrate the models.
            collect_static: A flag designating whether to collect static files.
            create_sites: A flag designating whether to create the django-sites.
            load_fixtures: An array of fixtures to load. None to skip.
        """

        if self.mode == "django":
            # NOTE: Imports come after django setup in server initialization.
            # pylint: disable=import-outside-toplevel
            from django.conf import settings
            from django.contrib.sites.models import Site

            # pylint: enable=import-outside-toplevel

            if self.db_engine == "sqlite":
                migrate = False
                create_sites = False
                load_fixtures = None

            if not self.django_dev_server_is_running:
                load_fixtures = None
                collect_static = False

            if migrate:
                call_django_command("migrate", interactive=False)
            if load_fixtures:
                call_django_command("load_fixtures", *load_fixtures)
            if collect_static:
                call_django_command("collectstatic", "--noinput", "--clear")
            if create_sites:

                def create_site(domain: str):
                    Site.objects.get_or_create(
                        domain=domain,
                        defaults={"name": settings.SERVICE_NAME},
                    )

                if t.cast(Env, settings.ENV) == "local":
                    create_site(domain=f"localhost:{settings.SERVICE_PORT}")
                    create_site(domain=f"127.0.0.1:{settings.SERVICE_PORT}")
                else:
                    create_site(domain=settings.SERVICE_DOMAIN)
                    create_site(domain=settings.SERVICE_HOST)

        if self.app_server_is_running:
            if self.mode == "celery":
                self.run_celery_worker_as_subprocess()

            super().run()

    def run_celery_worker_as_subprocess(self):
        """Starts a worker using the 'celery worker' command."""

        command = ["celery", f"--app={self.app_module}", "worker"]
        if self.workers:
            command.append(f"--concurrency={self.workers}")
        if self.log_level:
            command.append(f"--loglevel={self.log_level}")

            stdout, stderr = (None, None)  # Use defaults.
        else:
            stdout, stderr = (subprocess.DEVNULL, subprocess.DEVNULL)

        try:
            # pylint: disable-next=consider-using-with
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr)

            atexit.register(process.terminate)

            os.environ["SERVER_CELERY_WORKER_PID"] = str(process.pid)

        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(f"Error starting Celery worker: {ex}")
