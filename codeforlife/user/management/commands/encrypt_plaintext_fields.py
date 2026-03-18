"""
© Ocado Group
Created on 16/03/2026 at 10:58:04(+00:00).
"""

import typing as t

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import CharField, Model, TextField

from ....models.fields import EncryptedTextField, Sha256Field
from ....models.utils import is_real_model_class
from ....pprint import PrettyPrinter

PlaintextField: t.TypeAlias = t.Union[CharField, TextField]
FieldsToEncrypt: t.TypeAlias = t.List[
    t.Tuple[
        PlaintextField,
        t.Optional[EncryptedTextField],
        t.Optional[Sha256Field],
    ]
]


# pylint: disable-next=missing-class-docstring
class Command(BaseCommand):
    format_help = (
        "Arguments should be one or more Django app labels. "
        "For each model in each app, fields ending with '_plain' will be "
        "copied into matching '_enc' and '_hash' fields."
    )
    help = f"Encrypts and hashes plaintext fields for app models. {format_help}"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_labels", nargs="+", type=str, help=self.format_help
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=100,
            help="The number of records to process in each batch.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be updated without writing to the database.",
        )

    def _discover_model_fields(
        self,
        model_class: t.Type[Model],
        pprint: PrettyPrinter,
    ) -> FieldsToEncrypt:
        model_spec = (
            f"{model_class._meta.app_label}.{model_class._meta.model_name}"
        )
        fields_by_name = {
            field.name: field
            for field in model_class._meta.fields
            if isinstance(
                field, (CharField, TextField, EncryptedTextField, Sha256Field)
            )
        }

        fields_to_encrypt: FieldsToEncrypt = []
        for field_name, plain_field in fields_by_name.items():
            if not field_name.endswith("_plain"):
                continue
            if not isinstance(plain_field, (CharField, TextField)):
                continue

            field_name_prefix = field_name[: -len("_plain")]
            enc_field_name = f"{field_name_prefix}_enc"
            hash_field_name = f"{field_name_prefix}_hash"

            enc_field: t.Optional[EncryptedTextField] = None
            hash_field: t.Optional[Sha256Field] = None

            enc_field_obj = fields_by_name.get(enc_field_name)
            hash_field_obj = fields_by_name.get(hash_field_name)

            if isinstance(enc_field_obj, EncryptedTextField):
                enc_field = enc_field_obj
            elif enc_field_obj is not None:
                pprint(
                    "Skipping encrypted field due to type mismatch: "
                    + pprint.notice.apply(f"{model_spec}.{enc_field_name}")
                )

            if isinstance(hash_field_obj, Sha256Field):
                hash_field = hash_field_obj
            elif hash_field_obj is not None:
                pprint(
                    "Skipping hash field due to type mismatch: "
                    + pprint.notice.apply(f"{model_spec}.{hash_field_name}")
                )

            if enc_field is None and hash_field is None:
                if enc_field_obj is not None:
                    pprint(
                        "No valid target fields found for: "
                        + pprint.notice.apply(f"{model_spec}.{enc_field_name}")
                    )
                if hash_field_obj is not None:
                    pprint(
                        "No valid target fields found for: "
                        + pprint.notice.apply(f"{model_spec}.{hash_field_name}")
                    )
                continue

            target_fields = ", ".join(
                field_name
                for field_name in (enc_field_name, hash_field_name)
                if (field_name == enc_field_name and enc_field is not None)
                or (field_name == hash_field_name and hash_field is not None)
            )

            pprint(
                "Discovered field mapping: "
                + pprint.notice.apply(
                    f"{model_spec}.{field_name} -> {target_fields}"
                )
            )
            fields_to_encrypt.append((plain_field, enc_field, hash_field))

        return fields_to_encrypt

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def _encrypt_field(
        self,
        chunk_size: int,
        model_class: t.Type[Model],
        plain_field: PlaintextField,
        enc_field: t.Optional[EncryptedTextField],
        hash_field: t.Optional[Sha256Field],
        dry_run: bool,
        pprint: PrettyPrinter,
    ):
        if enc_field is None and hash_field is None:
            return

        models = model_class.objects.filter(  # type: ignore[attr-defined]
            **{f"{plain_field.name}__isnull": False}
        )
        model_count = models.count()

        if dry_run:
            pprint(f"Dry run: would update {model_count} records.")
            return

        for model_index, model in enumerate(models.iterator(chunk_size)):
            if model_index % chunk_size == 0:
                pprint(f"({model_index}/{model_count})")

            plaintext = getattr(model, plain_field.name)
            update_fields: t.List[str] = []
            if enc_field is not None:
                setattr(model, enc_field.name, plaintext)
                update_fields.append(enc_field.name)
            if hash_field is not None:
                setattr(model, hash_field.name, plaintext)
                update_fields.append(hash_field.name)
            model.save(update_fields=update_fields)

    def handle(self, *args, **options):
        app_labels: t.List[str] = options["app_labels"]
        chunk_size: int = options["chunk_size"]
        dry_run: bool = options["dry_run"]

        pprint = PrettyPrinter(write=self.stdout.write, name=self.__module__)

        for app_label in app_labels:
            with pprint.process(
                f"Processing app: {pprint.notice.apply(app_label)}"
            ) as app_pprint:
                app_config = apps.get_app_config(app_label)
                for model_class in app_config.get_models():
                    if not is_real_model_class(model_class):
                        app_pprint(
                            "Skipping non-real model: "
                            + pprint.notice.apply(
                                f"{model_class._meta.app_label}"
                                f".{model_class._meta.model_name}"
                            )
                        )
                        continue

                    with app_pprint.process(
                        "Encrypting model:"
                        f" {model_class._meta.app_label}"
                        f".{model_class._meta.model_name}"
                    ) as enc_model_pprint:
                        fields_to_encrypt = self._discover_model_fields(
                            model_class,
                            enc_model_pprint,
                        )

                        for (
                            plain_field,
                            enc_field,
                            hash_field,
                        ) in fields_to_encrypt:
                            target_field_names = [
                                field.name
                                for field in (enc_field, hash_field)
                                if field is not None
                            ]
                            with enc_model_pprint.process(
                                "Field: "
                                f"{plain_field.name} -> "
                                + ", ".join(target_field_names)
                            ) as enc_field_pprint:
                                self._encrypt_field(
                                    chunk_size,
                                    model_class,
                                    plain_field,
                                    enc_field,
                                    hash_field,
                                    dry_run,
                                    enc_field_pprint,
                                )
