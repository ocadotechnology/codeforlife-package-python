import typing as t

from django.db import migrations


def remove_plain_text_fields_and_rename_encrypted_text_fields(
    model_name: str, fields: t.List[str]
):
    """
    Removes all plaintext fields with the naming convention {field_name}_plain
    and renames the encrypted text fields with the naming convention
    {field_name}_enc to {field_name}.

    Args:
        model_name: The name of the model to modify.
        fields: A list of field names to process.

    Returns:
        A list of migration operations.
    """

    migrations_list = []
    for name in fields:
        plain_name = f"{name}_plain"
        enc_name = f"{name}_enc"

        migrations_list += [
            migrations.RemoveField(
                model_name=model_name,
                name=plain_name,
            ),
            migrations.RenameField(
                model_name=model_name,
                old_name=enc_name,
                new_name=name,
            ),
        ]

    return migrations_list


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_client_side_encryption_part_1"),
    ]

    operations = [
        # *remove_plain_text_fields_and_rename_encrypted_text_fields(
        #     "user",
        #     ["first_name", "last_name", "email", "username"],
        # ),
        # *remove_plain_text_fields_and_rename_encrypted_text_fields(
        #     "class",
        #     ["name", "access_code"],
        # ),
        # *remove_plain_text_fields_and_rename_encrypted_text_fields(
        #     "schoolteacherinvitation",
        #     [
        #         "token",
        #         "invited_teacher_first_name",
        #         "invited_teacher_last_name",
        #         "invited_teacher_email",
        #     ],
        # ),
        # *remove_plain_text_fields_and_rename_encrypted_text_fields(
        #     "school",
        #     ["name"],
        # ),
    ]
