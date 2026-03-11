import typing as t

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import CharField, Model, TextField

from ....models.fields import EncryptedTextField

FieldsToEncrypt: t.TypeAlias = t.List[
    t.Tuple[t.Union[CharField, TextField], EncryptedTextField]
]


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

    def _parse_arg(self, arg: str):
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
        fields_to_encrypt: FieldsToEncrypt = []
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

            # Get the encrypted field and validate its type.
            enc_field = model_class._meta.get_field(enc_field_name)
            if not isinstance(enc_field, EncryptedTextField):
                raise ValueError(
                    f"Encrypted field '{enc_field_name}' must be an "
                    "EncryptedTextField."
                )

            fields_to_encrypt.append((plain_field, enc_field))

        return model_class, fields_to_encrypt

    def _encrypt_fields(
        self, model_class: t.Type[Model], fields_to_encrypt: FieldsToEncrypt
    ):
        pass
        # Now you can iterate through the parsed arguments
        # for model_index, (model_spec, field_names) in enumerate(
        #     fields_to_encrypt.items(), start=1
        # ):
        #     app_label, model_name = model_spec.split(".", 1)

        #     self.stdout.write(
        #         self.style.SUCCESS(
        #             f"Processing model: {app_label}.{model_name}"
        #         )
        #     )

        #     self.stdout.write(f"{model_index}. {app_label}.{model_name}:")
        #     for field_index, field in enumerate(field_names, start=1):
        #         self.stdout.write(f"{model_index}.{field_index}. {field}")

        #     self.stdout.write(
        #         self.style.SUCCESS(f"Processed model: {app_label}.{model_name}")
        #     )

        # Here you would add your logic to get the model and encrypt the fields
        # For example:
        # try:
        #     model = apps.get_model(app_label, model_name)
        #     # ... encryption logic for model and field_names ...
        # except LookupError:
        #     self.stderr.write(f"Model '{model_spec}' not found.")

    def handle(self, *args, **options):
        for arg in options["model_fields"]:
            self.stdout.write(f"Parsing argument: {arg}")

            model_class, fields_to_encrypt = self._parse_arg(arg)

            self._encrypt_fields(model_class, fields_to_encrypt)
