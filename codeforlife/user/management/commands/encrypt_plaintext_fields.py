"""
© Ocado Group
Created on 16/03/2026 at 10:58:04(+00:00).
"""

import typing as t

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import CharField, Field, Model, Q, TextField

from ....encryption import create_dek
from ....models import BaseDataEncryptionKeyModel
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

    # pylint: disable-next=too-many-locals
    def _discover_model_fields(
        self,
        model_class: t.Type[Model],
        pprint: PrettyPrinter,
    ) -> FieldsToEncrypt:
        model_spec = (
            f"{model_class._meta.app_label}.{model_class._meta.model_name}"
        )
        plain_fields_by_name = {
            field.name: field
            for field in model_class._meta.fields
            if isinstance(field, (CharField, TextField))
            and field.name.endswith("_plain")
        }

        fields_to_encrypt: FieldsToEncrypt = []
        for field_name, plain_field in plain_fields_by_name.items():
            field_name_prefix = field_name[: -len("_plain")]
            enc_field_name = f"{field_name_prefix}_enc"
            hash_field_name = f"{field_name_prefix}_hash"

            enc_field: t.Optional[EncryptedTextField] = None
            hash_field: t.Optional[Sha256Field] = None

            try:
                enc_field_obj = model_class._meta.get_field(enc_field_name)
            except FieldDoesNotExist:
                enc_field_obj = None

            try:
                hash_field_obj = model_class._meta.get_field(hash_field_name)
            except FieldDoesNotExist:
                hash_field_obj = None

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
                + pprint.notice.apply(f"{field_name} -> {target_fields}")
            )
            fields_to_encrypt.append((plain_field, enc_field, hash_field))

        return fields_to_encrypt

    def _create_dek(
        self,
        chunk_size: int,
        dry_run: bool,
        model_class: t.Type[BaseDataEncryptionKeyModel],
        pprint: PrettyPrinter,
    ):
        models = model_class.objects.filter(  # type: ignore[misc]
            is_active=True, **{f"{model_class.DEK_FIELD}__isnull": True}
        )
        model_count = models.count()

        if dry_run:
            pprint(f"Dry run: would update {model_count} records.")
            return

        for model_index, model in enumerate(models.iterator(chunk_size)):
            if model_index % chunk_size == 0:
                pprint(f"({model_index}/{model_count})")

            setattr(model, model_class.DEK_FIELD, create_dek())
            model.save(update_fields=[model_class.DEK_FIELD])

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-locals
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
        def null_or_empty(field: Field, empty: t.Any):
            return Q(**{f"{field.name}__isnull": True}) | Q(
                **{f"{field.name}": empty}
            )

        if enc_field is not None and hash_field is not None:
            q = null_or_empty(enc_field, b"") | null_or_empty(hash_field, "")
        elif enc_field is not None:
            q = null_or_empty(enc_field, b"")
        elif hash_field is not None:
            q = null_or_empty(hash_field, "")
        else:
            return

        models = model_class.objects.exclude(  # type: ignore[attr-defined]
            null_or_empty(plain_field, "")
        ).filter(q)
        if model_class._meta.model_name in [
            "school",
            "user",
            "schoolteacherinvitation",
            "class",
        ]:
            models = models.exclude(is_active=False)
        model_count = models.count()

        if dry_run:
            pprint(f"Dry run: would update {model_count} records.")
            return

        for model_index, model in enumerate(models.iterator(chunk_size)):
            if model_index % chunk_size == 0:
                pprint(f"({model_index}/{model_count})")

            plaintext = getattr(model, plain_field.name)
            field_property_name = plain_field.name.removesuffix(
                "_plain"
            ).removeprefix("_")
            setattr(model, field_property_name, plaintext)

            update_fields: t.List[str] = []
            if enc_field is not None:
                update_fields.append(enc_field.name)
            if hash_field is not None:
                update_fields.append(hash_field.name)
            model.save(update_fields=update_fields)

    # pylint: disable-next=too-many-locals
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
                model_classes = [
                    model_class
                    for model_class in app_config.get_models()
                    if is_real_model_class(model_class)
                ]

                # First create any missing DEKs for the models, so they're
                # available for encrypting fields in the next step.
                for model_class in model_classes:
                    if issubclass(model_class, BaseDataEncryptionKeyModel):
                        with app_pprint.process(
                            "Creating DEK: "
                            + app_pprint.notice.apply(
                                f"{model_class._meta.app_label}"
                                f".{model_class._meta.model_name}"
                            )
                        ) as dek_pprint:
                            self._create_dek(
                                chunk_size, dry_run, model_class, dek_pprint
                            )

                for model_class in model_classes:
                    with app_pprint.process(
                        "Encrypting model: "
                        + app_pprint.notice.apply(
                            f"{model_class._meta.app_label}"
                            f".{model_class._meta.model_name}"
                        )
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
                                + enc_model_pprint.notice.apply(
                                    f"{plain_field.name} -> "
                                    + ", ".join(target_field_names)
                                )
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
