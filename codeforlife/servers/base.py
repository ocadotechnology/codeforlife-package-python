"""
© Ocado Group
Created on 31/03/2025 at 09:04:19(+01:00).
"""

import os
import sys


# pylint: disable-next=too-few-public-methods
class BaseServer:
    """The base server which all servers must inherit."""

    main_module: str = "application"  # The dot-path of the main module.

    @classmethod
    def in_main_process(cls):
        """Whether or not this server is running in the main process."""
        file_name = os.path.basename(sys.argv[0])
        return os.path.splitext(file_name)[0] == cls.main_module
