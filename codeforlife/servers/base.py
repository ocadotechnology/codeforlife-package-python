"""
© Ocado Group
Created on 31/03/2025 at 09:04:19(+01:00).
"""

import os
import sys


# pylint: disable-next=too-few-public-methods
class BaseServer:
    """The base server which all servers must inherit."""

    # The entrypoint module.
    main_module = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    # The dot-path of the application module.
    app_module: str = "application"

    @classmethod
    def app_server_is_running(cls):
        """Whether or not the app server is running."""
        return (
            cls.main_module == cls.app_module
            and os.environ["SERVER"] == cls.__name__
        )
