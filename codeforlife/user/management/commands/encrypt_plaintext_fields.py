"""
© Ocado Group
Created on 16/03/2026 at 10:58:04(+00:00).
"""

import typing as t

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import CharField, Model, TextField

from ....models.fields import EncryptedTextField
from ....pprint import PrettyPrinter

PlaintextField: t.TypeAlias = t.Union[CharField, TextField]
FieldsToEncrypt: t.TypeAlias = t.Dict[PlaintextField, EncryptedTextField]


# pylint: disable-next=missing-class-docstring
class Command(BaseCommand):
    format_help = (
        "Arguments should be in the format 'app_label.ModelName="
        "plain_field1:encrypted_text_field1,"
        "plain_field2:encrypted_text_field2'."
    )
    help = f"Encrypts plaintext fields for specified models. {format_help}"

    def add_arguments(self, parser):
        parser.add_argument(
            "model_fields", nargs="+", type=str, help=self.format_help
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=100,
            help="The number of records to process in each batch.",
        )

    def _parse_arg(self, arg: str, pprint: PrettyPrinter):
        # Split the argument into model specification and field name pairs.
        if not "=" in arg:
            raise ValueError(self.format_help)
        model_spec, field_csv = arg.split("=", 1)

        # Retrieve the model class based on the app and model name.
        if "." not in model_spec:
            raise ValueError(self.format_help)
        app_label, model_name = model_spec.split(".", 1)
        model_class: t.Type[Model] = apps.get_model(app_label, model_name)
        pprint(f"Found model: {pprint.notice.apply(model_spec)}")

        # Parse the field name pairs and validate their existence in the model.
        fields_to_encrypt: FieldsToEncrypt = {}
        for field_name_pair in field_csv.split(","):
            # Split the field name pair.
            if ":" not in field_name_pair:
                raise ValueError(self.format_help)
            plain_field_name, enc_field_name = field_name_pair.split(":", 1)

            # Strip and validate field names.
            plain_field_name = plain_field_name.strip()
            enc_field_name = enc_field_name.strip()
            if not plain_field_name or not enc_field_name:
                raise ValueError(self.format_help)

            # Get the plaintext field and validate its type.
            plain_field = model_class._meta.get_field(plain_field_name)
            if not isinstance(plain_field, (CharField, TextField)):
                raise ValueError(
                    f"Plaintext field '{plain_field_name}' must be "
                    "a CharField or TextField."
                )
            if plain_field in fields_to_encrypt:
                raise ValueError(
                    f"Duplicate plaintext field '{plain_field_name}' in "
                    "argument."
                )
            pprint(
                "Found plaintext field: "
                + pprint.notice.apply(f"{model_spec}.{plain_field_name}")
            )

            # Get the encrypted field and validate its type.
            enc_field = model_class._meta.get_field(enc_field_name)
            if not isinstance(enc_field, EncryptedTextField):
                raise ValueError(
                    f"Encrypted field '{enc_field_name}' must be an "
                    "EncryptedTextField."
                )
            if enc_field in fields_to_encrypt.values():
                raise ValueError(
                    f"Duplicate encrypted field '{enc_field_name}' in "
                    "argument."
                )
            pprint(
                "Found encrypted field: "
                + pprint.notice.apply(f"{model_spec}.{enc_field_name}")
            )

            fields_to_encrypt[plain_field] = enc_field

        return model_class, fields_to_encrypt

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def _encrypt_field(
        self,
        chunk_size: int,
        model_class: t.Type[Model],
        plain_field: PlaintextField,
        enc_field: EncryptedTextField,
        pprint: PrettyPrinter,
    ):
        models = model_class.objects.filter(  # type: ignore[attr-defined]
            **{f"{plain_field.name}__isnull": False}
        )
        model_count = models.count()
        for model_index, model in enumerate(models.iterator(chunk_size)):
            if model_index % chunk_size == 0:
                pprint(f"({model_index}/{model_count})")

            plaintext = getattr(model, plain_field.name)
            setattr(model, enc_field.name, plaintext)
            model.save(update_fields=[enc_field.name])

    def handle(self, *args, **options):
        model_fields: t.List[str] = options["model_fields"]
        chunk_size: int = options["chunk_size"]

        pprint = PrettyPrinter(write=self.stdout.write, name=self.__module__)

        for arg in model_fields:
            with pprint.process(
                "Processing argument: "
                f'"{arg if len(arg) <= 50 else f"{arg[:37]}...{arg[-10:]}"}"'
            ) as arg_pprint:
                with arg_pprint.process("Parsing argument") as parse_pprint:
                    model_class, fields_to_encrypt = self._parse_arg(
                        arg, parse_pprint
                    )

                with arg_pprint.process(
                    "Encrypting model:"
                    f" {model_class._meta.app_label}"
                    f".{model_class._meta.model_name}"
                ) as enc_model_pprint:
                    for plain_field, enc_field in fields_to_encrypt.items():
                        with enc_model_pprint.process(
                            f"Field: {plain_field.name} -> {enc_field.name}"
                        ) as enc_field_pprint:
                            self._encrypt_field(
                                chunk_size,
                                model_class,
                                plain_field,
                                enc_field,
                                enc_field_pprint,
                            )
