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

    def __init__(self, main_module: str = "application"):
        """Initialize a base-server instance.

        Args:
            main_module: The dot-path of the main module.
        """
        self.main_module = main_module

    @cached_property
    def in_main_process(self):
        """Whether or not this server is running in the main process."""
        file_name = os.path.basename(sys.argv[0])
        return os.path.splitext(file_name)[0] == self.main_module
