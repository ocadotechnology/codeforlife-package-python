import typing as t

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import CharField, Model, TextField

from ....models.fields import EncryptedTextField
from ....pprint import PrettyPrinter

FieldsToEncrypt: t.TypeAlias = t.Dict[
    t.Union[CharField, TextField], EncryptedTextField
]


# pylint: disable-next=missing-class-docstring
class Command(BaseCommand):
    format_help = (
        "Arguments should be in the format 'app_label.ModelName="
        "plain_field1:encrypted_text_field1,"
        "plain_field2:encrypted_text_field2'."
    )
    help = f"Encrypts plaintext fields for specified models. {format_help}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pprint = PrettyPrinter(write=self.stdout.write)

    def add_arguments(self, parser):
        parser.add_argument(
            "model_fields", nargs="+", type=str, help=self.format_help
        )

    def _parse_arg(self, arg: str):
        self.pprint.indent(
            1, ending=self.pprint.bold("Parsing ... ", write=False)
        )

        # Split the argument into model specification and field name pairs.
        if not "=" in arg:
            raise ValueError(self.format_help)
        model_spec, field_csv = arg.split("=", 1)

        # Retrieve the model class based on the app and model name.
        if "." not in model_spec:
            raise ValueError(self.format_help)
        app_label, model_name = model_spec.split(".", 1)
        model_class: t.Type[Model] = apps.get_model(app_label, model_name)

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

            fields_to_encrypt[plain_field] = enc_field

        self.pprint.success("Done")

        return model_class, fields_to_encrypt

    def _encrypt_fields(
        self, model_class: t.Type[Model], fields_to_encrypt: FieldsToEncrypt
    ):
        self.pprint.indent(
            1, ending=self.pprint.bold("Encrypting fields:\n", write=False)
        )

        for plain_field, enc_field in fields_to_encrypt.items():
            self.pprint.indent(
                2, ending=f"{plain_field.name} -> {enc_field.name} ... "
            )

            # TODO: encrypt the plaintext field values and save them to the
            # encrypted field.

            self.pprint.success("Done")

    def handle(self, *args, **options):
        for arg in options["model_fields"]:
            self.pprint.divider()
            self.pprint.bold("Processing argument:", ending=" ")
            self.pprint.write(
                f'"{arg if len(arg) <= 50 else arg[:37] + "..." + arg[-10:]}".'
            )

            model_class, fields_to_encrypt = self._parse_arg(arg)

            self._encrypt_fields(model_class, fields_to_encrypt)
