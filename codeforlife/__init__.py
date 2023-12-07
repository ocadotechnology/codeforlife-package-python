from pathlib import Path

import django_stubs_ext

from .version import __version__

# ------------------------------------------------------------------------------
# Package setup.
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("data")

django_stubs_ext.monkeypatch()

# ------------------------------------------------------------------------------

# NOTE: These imports need to come after the package setup.
# pylint: disable=wrong-import-position
from . import kurono, service, user
