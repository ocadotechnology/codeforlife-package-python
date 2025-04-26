"""
© Ocado Group
Created on 31/03/2025 at 09:04:19(+01:00).
"""

import os
import sys
from functools import cached_property


# pylint: disable-next=too-few-public-methods
class BaseServer:
    """The base server which all servers must inherit."""

    # The entrypoint module.
    main_module = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    # The dot-path of the application module.
    app_module: str = "application"

    @cached_property
    def app_server_is_running(self):
        """Whether or not the app server is running."""
        return (
            self.main_module == self.app_module
            and os.environ["SERVER"] == self.__class__.__name__
        )
