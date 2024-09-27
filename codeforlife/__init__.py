"""
© Ocado Group
Created on 20/02/2024 at 09:28:27(+00:00).
"""

from pathlib import Path

from .version import __version__

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("data")
USER_DIR = BASE_DIR.joinpath("user")
