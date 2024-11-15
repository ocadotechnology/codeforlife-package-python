"""
© Ocado Group
Created on 10/06/2024 at 10:44:45(+01:00).
"""

import os
import typing as t

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand


# pylint: disable-next=missing-class-docstring
class LoadFixtures(BaseCommand):
    help = "Loads all the fixtures of the specified apps."

    required_app_labels: t.Set[str] = set()

    def add_arguments(self, parser):
        parser.add_argument("app_labels", nargs="*", type=str)

    def handle(self, *args, **options):
        fixture_labels: t.List[str] = []
        for app_label in {*options["app_labels"], *self.required_app_labels}:
            app_config = apps.app_configs[app_label]
            fixtures_path = os.path.join(app_config.path, "fixtures")

            self.stdout.write(f"{app_label} fixtures ({fixtures_path}):")
            for fixture_label in os.listdir(fixtures_path):
                if fixture_label in fixture_labels:
                    self.stderr.write(f"Duplicate fixture: {fixture_label}")
                    return

                self.stdout.write(f"    - {fixture_label}")
                fixture_labels.append(fixture_label)

            self.stdout.write()

        call_command("loaddata", *fixture_labels)
