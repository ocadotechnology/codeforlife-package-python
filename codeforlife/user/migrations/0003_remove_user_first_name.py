import typing as t

from codeforlife.models.fields import EncryptedTextField
from django.apps.registry import Apps
from django.db import migrations

if t.TYPE_CHECKING:
    from django.db.models import Model


def encrypt_field(model_name: str, name: str, temp_name: str):
    def code(apps: Apps, schema_editor):
        model_class: Model = apps.get_model("codeforlife.user", model_name)

        models = model_class.objects.filter(**{f"{name}__isnull": False})
        for model in models:
            value = getattr(model, name)
            setattr(model, temp_name, value)
            model.save(update_fields=[temp_name])

    return code


def decrypt_field(model_name: str, name: str, temp_name: str):
    def reverse_code(apps: Apps, schema_editor):
        model_class: Model = apps.get_model("codeforlife.user", model_name)

        models = model_class.objects.filter(**{f"{temp_name}__isnull": False})
        for model in models:
            value = getattr(model, temp_name)
            setattr(model, name, value)
            model.save(update_fields=[name])

    return reverse_code


def create_migrations(model_name: str, name: str, verbose_name: str):
    """Creates a list of migrations to encrypt a field in the database."""

    temp_name = f"_{name}"

    return [
        migrations.AddField(
            model_name=model_name,
            name=temp_name,
            field=EncryptedTextField(
                associated_data=name,
                db_column=temp_name,
                default=None,
                verbose_name=verbose_name,
            ),
        ),
        migrations.RunPython(
            code=encrypt_field(model_name, name, temp_name),
            reverse_code=decrypt_field(model_name, name, temp_name),
        ),
        migrations.RemoveField(
            model_name=model_name,
            name=name,
        ),
        migrations.RenameField(
            model_name=model_name,
            old_name=temp_name,
            new_name=name,
        ),
        migrations.AlterField(
            model_name=model_name,
            name=name,
            field=EncryptedTextField(
                associated_data=name,
                db_column=name,
                default=None,
                verbose_name=verbose_name,
            ),
        ),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_user_managers_school_dek_user_dek"),
    ]

    operations = [
        *create_migrations("user", "first_name", "first name"),
        *create_migrations("user", "last_name", "last name"),
        *create_migrations("user", "email", "email address"),
        *create_migrations("user", "username", "username"),
        *create_migrations("class", "name", "name"),
        *create_migrations("class", "access_code", "access code"),
        *create_migrations("schoolteacherinvitation", "token", "token"),
        *create_migrations(
            "schoolteacherinvitation",
            "invited_teacher_first_name",
            "invited teacher first name",
        ),
        *create_migrations(
            "schoolteacherinvitation",
            "invited_teacher_last_name",
            "invited teacher last name",
        ),
        *create_migrations(
            "schoolteacherinvitation",
            "invited_teacher_email",
            "invited teacher email",
        ),
        *create_migrations("school", "name", "name"),
    ]
