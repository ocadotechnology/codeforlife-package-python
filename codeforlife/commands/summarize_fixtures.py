"""
© Ocado Group
Created on 22/02/2024 at 09:24:27(+00:00).
"""

import json
import os
import typing as t
from dataclasses import dataclass
from itertools import groupby

from django.apps import apps
from django.core.management.base import BaseCommand

from ..types import JsonDict


@dataclass(frozen=True)
class Fixture:
    """A data model fixture."""

    model: str
    pk: t.Any
    fields: JsonDict


FixtureDict = t.Dict[str, t.List[Fixture]]


# pylint: disable-next=missing-class-docstring
class SummarizeFixtures(BaseCommand):
    help = "Summarizes all the listed fixtures."

    required_app_labels: t.Set[str] = set()

    def add_arguments(self, parser):
        parser.add_argument("app_labels", nargs="*", type=str)

    def _write_pks_per_model(self, fixtures: t.List[Fixture], indents: int = 0):
        def get_model(fixture: Fixture):
            return fixture.model.lower()

        fixtures.sort(key=get_model)

        self.stdout.write(f'{"    " * indents}Primary keys per model:')

        for model, group in groupby(fixtures, key=get_model):
            pks = [fixture.pk for fixture in group]
            pks.sort()

            self.stdout.write(f'{"    " * (indents + 1)}- {model}: {pks}')

    def write_pks_per_model(self, fixtures: FixtureDict):
        """Write all the sorted primary keys per model."""
        self._write_pks_per_model(
            [
                fixture
                for file_fixtures in fixtures.values()
                for fixture in file_fixtures
            ]
        )

    def write_pks_per_file(self, fixtures: FixtureDict):
        """Write all the sorted primary keys per file, per model."""
        self.stdout.write("Primary keys per file:")

        for file, file_fixtures in fixtures.items():
            self.stdout.write(f"    - {file}")
            self._write_pks_per_model(file_fixtures, indents=2)

    def handle(self, *args, **options):
        fixtures: FixtureDict = {}
        for app_label in {*options["app_labels"], *self.required_app_labels}:
            app_config = apps.app_configs[app_label]
            fixtures_path = os.path.join(app_config.path, "fixtures")

            for fixture_name in os.listdir(fixtures_path):
                fixture_path = os.path.join(fixtures_path, fixture_name)
                with open(fixture_path, "r", encoding="utf-8") as fixture:
                    fixtures[fixture_path] = [
                        Fixture(**fixture) for fixture in json.load(fixture)
                    ]

        self.write_pks_per_model(fixtures)
        self.stdout.write()
        self.write_pks_per_file(fixtures)
