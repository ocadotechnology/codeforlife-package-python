"""
© Ocado Group
Created on 28/10/2024 at 16:19:47(+00:00).
"""

import multiprocessing
import os

from django.core.asgi import get_asgi_application
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from gunicorn.app.base import BaseApplication  # type: ignore[import-untyped]


# pylint: disable-next=abstract-method
class DjangoApplication(BaseApplication):
    """A server for a Django app.

    Based off of:
    https://gist.github.com/Kludex/c98ed6b06f5c0f89fd78dd75ef58b424
    https://docs.gunicorn.org/en/stable/custom.html
    """

    def __init__(self, workers: int = int(os.getenv("WORKERS", "0"))):
        """Initialize a Django app.

        Before starting, all migrations will be applied.

        Args:
            workers: The number of Gunicorn workers. 0 will auto-calculate.
        """

        call_command("migrate", interactive=False)

        self.options = {
            "bind": "0.0.0.0:8080",
            # https://docs.gunicorn.org/en/stable/design.html#how-many-workers
            "workers": workers or (multiprocessing.cpu_count() * 2) + 1,
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        self.application = get_asgi_application()

        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    @classmethod
    def handle_startup(cls, name: str):
        """Handle the startup procedure of a Django app.

        Examples:
            ```
            import os
            from codeforlife.apps import DjangoApplication

            # Make sure to set this before starting the Django app!
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

            django_app = DjangoApplication.handle_startup(__name__)
            ```

        Args:
            name: The name of the file calling this function.

        Returns:
            An instance of a Django app.
        """

        if name == "__main__":
            cls().run()
        else:
            return get_wsgi_application()

        return None
