import typing as t

from django.db import migrations, models

from ...models.fields import (
    DataEncryptionKeyField,
    EncryptedTextField,
    Sha256Field,
)


def rename_plain_text_fields_and_create_encrypted_text_fields(
    model_name: str, fields: t.Dict[str, str]
):
    """
    Renames all plaintext fields with the naming convention {field_name}_plain
    and creates new encrypted text fields with the naming convention
    {field_name}_enc.

    Args:
        model_name: The name of the model to modify.
        fields: A dictionary mapping field names to their verbose names.

    Returns:
        A list of migration operations.
    """

    migrations_list = []
    for name, verbose_name in fields.items():
        migrations_list += [
            # Rename the plain text field.
            migrations.RenameField(
                model_name=model_name,
                old_name=name,
                new_name=f"{name}_plain",
            ),
            # Add an encrypted text field.
            migrations.AddField(
                model_name=model_name,
                name=f"{name}_enc",
                field=EncryptedTextField(
                    associated_data=name,
                    null=True,
                    verbose_name=verbose_name,
                ),
            ),
        ]

    return migrations_list


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_user_proxies_and_new_models"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254,
                null=True,
                unique=True,
                verbose_name="email address",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="email_hash",
            field=Sha256Field(
                unique=True,
                null=True,
                editable=False,
                max_length=64,
                verbose_name="email hash",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="first_name_hash",
            field=Sha256Field(
                null=True,
                editable=False,
                max_length=64,
                verbose_name="first name hash",
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="access_code_hash",
            field=Sha256Field(
                null=True,
                editable=False,
                max_length=64,
                verbose_name="access code hash",
            ),
        ),
        migrations.AddField(
            model_name="school",
            name="dek",
            field=DataEncryptionKeyField(
                editable=False,
                help_text="The encrypted data encryption key (DEK) for this model.",
                null=True,
                verbose_name="data encryption key",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="dek",
            field=DataEncryptionKeyField(
                editable=False,
                help_text="The encrypted data encryption key (DEK) for this model.",
                null=True,
                verbose_name="data encryption key",
            ),
        ),
        *rename_plain_text_fields_and_create_encrypted_text_fields(
            "user",
            {
                "first_name": "first name",
                "last_name": "last name",
                "email": "email address",
            },
        ),
        *rename_plain_text_fields_and_create_encrypted_text_fields(
            "class",
            {"name": "name", "access_code": "access code"},
        ),
        *rename_plain_text_fields_and_create_encrypted_text_fields(
            "schoolteacherinvitation",
            {
                "token": "token",
                "invited_teacher_first_name": "invited teacher first name",
                "invited_teacher_last_name": "invited teacher last name",
                "invited_teacher_email": "invited teacher email",
            },
        ),
        *rename_plain_text_fields_and_create_encrypted_text_fields(
            "school",
            {"name": "name"},
        ),
    ]
