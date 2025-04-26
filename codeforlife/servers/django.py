"""
© Ocado Group
Created on 28/10/2024 at 16:19:47(+00:00).
"""

import multiprocessing
import os
import sys
import typing as t
from functools import cached_property

from django import setup
from django.core.asgi import get_asgi_application
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from gunicorn.app.base import BaseApplication  # type: ignore[import-untyped]

from .base import BaseServer


# pylint: disable-next=abstract-method
class DjangoServer(BaseServer, BaseApplication):
    """A server for a Django app.

    Based off of:
    https://gist.github.com/Kludex/c98ed6b06f5c0f89fd78dd75ef58b424
    https://docs.gunicorn.org/en/stable/custom.html
    """

    # The dot-path of Django's manage module.
    django_manage_module: str = "manage"

    # pylint: disable-next=too-many-arguments,dangerous-default-value
    def __init__(
        self,
        auto_run: bool = True,
        workers: int = int(os.getenv("WORKERS", "0")),
        settings_module: str = "settings",
        auto_migrate: bool = True,
        auto_collect: bool = True,
        auto_load_fixtures: t.Optional[t.Set[str]] = {"src"},
    ):
        # pylint: disable=line-too-long
        """Initialize a Django app.

        Examples:
            ```
            from codeforlife.apps import DjangoServer

            django_app = DjangoServer().wsgi_app
            ```

        Args:
            auto_run: A flag designating whether to auto-run the server.
            workers: The number of Gunicorn workers. 0 will auto-calculate.
            settings_module: The dot-path to the settings module.
            auto_migrate: A flag designating whether to auto-migrate the models.
            auto_collect: A flag designating whether to auto-collect static files.
            auto_load_fixtures: An array of fixtures to auto-load. None to skip.
        """
        # pylint: enable=line-too-long

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

        setup()

        if auto_migrate and (
            self.app_server_is_running or self.django_dev_server_is_running
        ):
            call_command("migrate", interactive=False)

        if auto_load_fixtures and self.django_dev_server_is_running:
            call_command("load_fixtures", *auto_load_fixtures)

        if auto_collect and self.django_dev_server_is_running:
            call_command("collectstatic", "--noinput", "--clear")

        self.options = {
            "bind": "0.0.0.0:8080",
            # https://docs.gunicorn.org/en/stable/design.html#how-many-workers
            "workers": workers or (multiprocessing.cpu_count() * 2) + 1,
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        self.asgi_app = get_asgi_application()
        self.wsgi_app = get_wsgi_application()

        super().__init__()

        if auto_run and self.app_server_is_running:
            self.run()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.asgi_app

    @cached_property
    def django_dev_server_is_running(self):
        """Whether or not the Django development server is running."""
        return (
            self.main_module == self.django_manage_module
            and sys.argv[1] == "runserver"
        )
