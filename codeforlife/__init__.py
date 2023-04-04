from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("data")


from .version import __version__

from . import user
