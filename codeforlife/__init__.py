"""
© Ocado Group
Created on 09/12/2023 at 11:02:54(+00:00).

Entry point to the Code for Life package.
"""

import typing as t
from pathlib import Path

from .version import __version__

# ------------------------------------------------------------------------------
# Package setup.
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("data")

if t.TYPE_CHECKING:
    import django_stubs_ext

    django_stubs_ext.monkeypatch()

# ------------------------------------------------------------------------------

# NOTE: These imports need to come after the package setup.
# pylint: disable=wrong-import-position
from . import kurono, service, user
