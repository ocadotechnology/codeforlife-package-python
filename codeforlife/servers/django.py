"""
© Ocado Group
Created on 28/10/2024 at 16:19:47(+00:00).
"""

import multiprocessing
import os

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

    def __init__(
        self,
        main_module: str = "application",
        workers: int = int(os.getenv("WORKERS", "0")),
    ):
        """Initialize a Django app.

        Before starting, all migrations will be applied.

        Examples:
            ```
            from codeforlife.apps import DjangoServer

            # Make sure to set up Django before initializing!
            DjangoServer.setup()

            django_app = DjangoServer().wsgi_app
            ```

        Args:
            main_module: The dot-path of the main module.
            workers: The number of Gunicorn workers. 0 will auto-calculate.
        """

        self.options = {
            "bind": "0.0.0.0:8080",
            # https://docs.gunicorn.org/en/stable/design.html#how-many-workers
            "workers": workers or (multiprocessing.cpu_count() * 2) + 1,
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        self.asgi_app = get_asgi_application()
        self.wsgi_app = get_wsgi_application()

        super().__init__(main_module)

        # Auto-run if in main process.
        if self.in_main_process:
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

    @staticmethod
    def setup(settings_module: str = "settings"):
        """Set up the Django app.

        Args:
            settings_module: The dot-path to the settings module.
        """

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

        setup()

        call_command("migrate", interactive=False)
