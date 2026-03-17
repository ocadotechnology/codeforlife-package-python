from django.db import migrations

from ...models.fields import EncryptedTextField, Sha256Field

user_migrations = [
    migrations.AlterField(
        model_name="user",
        name="email_hash",
        field=Sha256Field(
            db_column="email_hash",
            editable=False,
            max_length=64,
            null=True,
            unique=True,
            verbose_name="email hash",
        ),
    ),
    migrations.RenameField(
        model_name="user",
        old_name="email_hash",
        new_name="_email_hash",
    ),
    migrations.AlterField(
        model_name="user",
        name="email_enc",
        field=EncryptedTextField(
            associated_data="email",
            db_column="email",
            null=True,
            verbose_name="email address",
        ),
    ),
    migrations.RenameField(
        model_name="user",
        old_name="email_enc",
        new_name="_email",
    ),
    migrations.RemoveField(
        model_name="user",
        name="email_plain",
    ),
    migrations.AlterField(
        model_name="user",
        name="first_name_hash",
        field=Sha256Field(
            db_column="first_name_hash",
            editable=False,
            max_length=64,
            null=True,
            verbose_name="first name hash",
        ),
    ),
    migrations.RenameField(
        model_name="user",
        old_name="first_name_hash",
        new_name="_first_name_hash",
    ),
    migrations.AlterField(
        model_name="user",
        name="first_name_enc",
        field=EncryptedTextField(
            associated_data="first_name",
            db_column="first_name",
            null=True,
            verbose_name="first name",
        ),
    ),
    migrations.RenameField(
        model_name="user",
        old_name="first_name_enc",
        new_name="_first_name",
    ),
    migrations.RemoveField(
        model_name="user",
        name="first_name_plain",
    ),
    migrations.RenameField(
        model_name="user",
        old_name="last_name_enc",
        new_name="last_name",
    ),
    migrations.RemoveField(
        model_name="user",
        name="last_name_plain",
    ),
]

class_migrations = [
    migrations.AlterField(
        model_name="class",
        name="access_code_hash",
        field=Sha256Field(
            db_column="access_code_hash",
            editable=False,
            max_length=64,
            null=True,
            verbose_name="access code hash",
        ),
    ),
    migrations.RenameField(
        model_name="class",
        old_name="access_code_hash",
        new_name="_access_code_hash",
    ),
    migrations.AlterField(
        model_name="class",
        name="access_code_enc",
        field=EncryptedTextField(
            associated_data="access_code",
            db_column="access_code",
            null=True,
            verbose_name="access code",
        ),
    ),
    migrations.RenameField(
        model_name="class",
        old_name="access_code_enc",
        new_name="_access_code",
    ),
    migrations.RemoveField(
        model_name="class",
        name="access_code_plain",
    ),
    migrations.RenameField(
        model_name="class",
        old_name="name_enc",
        new_name="name",
    ),
    migrations.RemoveField(
        model_name="class",
        name="name_plain",
    ),
]

school_migrations = [
    migrations.RenameField(
        model_name="school",
        old_name="name_enc",
        new_name="name",
    ),
    migrations.RemoveField(
        model_name="school",
        name="name_plain",
    ),
]

school_teacher_invitation_migrations = [
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_email_enc",
        new_name="invited_teacher_email",
    ),
    migrations.RemoveField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_email_plain",
    ),
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_first_name_enc",
        new_name="invited_teacher_first_name",
    ),
    migrations.RemoveField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_first_name_plain",
    ),
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_last_name_enc",
        new_name="invited_teacher_last_name",
    ),
    migrations.RemoveField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_last_name_plain",
    ),
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="token_enc",
        new_name="token",
    ),
    migrations.RemoveField(
        model_name="schoolteacherinvitation",
        name="token_plain",
    ),
]


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_client_side_encryption_part_1"),
    ]

    operations = [
        *user_migrations,
        *class_migrations,
        *school_migrations,
        *school_teacher_invitation_migrations,
    ]
