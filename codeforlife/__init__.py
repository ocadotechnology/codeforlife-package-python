"""
© Ocado Group
Created on 20/02/2024 at 09:28:27(+00:00).
"""

import os
import sys
import typing as t
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from .types import Env

# Do NOT set manually!
# This is auto-updated by python-semantic-release in the pipeline.
__version__ = "0.28.3"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("data")
TEMPLATES_DIR = BASE_DIR.joinpath("templates")
USER_DIR = BASE_DIR.joinpath("user")


if t.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


# pylint: disable-next=too-few-public-methods
class Secrets(SimpleNamespace):
    """The secrets for this service.

    If a key does not exist, the value None will be returned.
    """

    def __getattribute__(self, name: str) -> t.Optional[str]:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return None


def set_up_settings(service_base_dir: Path, service_name: str):
    """Set up the settings for the service.

    *This needs to be called before importing the CFL settings!*

    To expose a secret to your Django project, you'll need to create a setting
    for it following Django's conventions.

    Examples:
        ```
        from codeforlife import set_up_settings

        # Must set up settings before importing them!
        secrets = set_up_settings(BASE_DIR, service_name="my-service")

        from codeforlife.settings import *

        # Expose secret to django project.
        SECRET_KEY = secrets.SECRET_KEY
        ```

    Args:
        service_base_dir: The base directory of the service.
        service_name: The name of the service.

    Returns:
        The secrets. These are not loaded as environment variables so that 3rd
        party packages cannot read them.
    """

    # Validate CFL settings have not been imported yet.
    if "codeforlife.settings" in sys.modules:
        raise ImportError(
            "You must set up the CFL settings before importing them."
        )

    # pylint: disable-next=import-outside-toplevel
    from dotenv import dotenv_values, load_dotenv

    # Set required environment variables.
    os.environ["SERVICE_BASE_DIR"] = str(service_base_dir)
    os.environ["SERVICE_NAME"] = service_name

    # Get environment name.
    os.environ.setdefault("ENV", "local")
    env = t.cast(Env, os.environ["ENV"])

    # Load environment variables.
    load_dotenv(service_base_dir / f"env/.env.{env}", override=False)
    load_dotenv(service_base_dir / "env/.env", override=False)

    # Get secrets.
    if env == "local":
        secrets_path = service_base_dir / "env/.env.local.secrets"
        # TODO: move this to the dev container setup script.
        if not os.path.exists(secrets_path):
            # pylint: disable=line-too-long
            secrets_file_comment = (
                "# 📝 Local Secret Variables 📝\n"
                "# These secret variables are only loaded in your local environment (on your PC).\n"
                "#\n"
                "# This file is git-ignored intentionally to keep these variables a secret.\n"
                "#\n"
                "# 🚫 DO NOT PUSH SECRETS TO THE CODE REPO 🚫\n"
                "\n"
            )
            # pylint: enable=line-too-long

            with open(secrets_path, "w+", encoding="utf-8") as secrets_file:
                secrets_file.write(secrets_file_comment)

        secrets = dotenv_values(secrets_path)
        secrets.setdefault(
            # NOTE: This is only used locally for testing purposes.
            "SECRET_KEY",
            "XTgWqMlZCMI_E5BvCArkif9nrJIIhe_6Ic6Q_UcWJDk=",
        )
    else:
        # pylint: disable-next=import-outside-toplevel
        import boto3

        s3: "S3Client" = boto3.client("s3")
        secrets_object = s3.get_object(
            Bucket=os.environ["aws_s3_app_bucket"],
            Key=(
                os.environ["aws_s3_app_folder"]
                + f"/secure/.env.secrets.{service_name}"
            ),
        )

        secrets = dotenv_values(
            stream=StringIO(secrets_object["Body"].read().decode("utf-8"))
        )

    return Secrets(**secrets)
