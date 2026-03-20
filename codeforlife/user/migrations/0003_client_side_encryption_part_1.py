from django.db import migrations

from ...models.fields import (
    DataEncryptionKeyField,
    EncryptedTextField,
    Sha256Field,
)

user_migrations = [
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
    # Username
    migrations.RenameField(
        model_name="user",
        old_name="username",
        new_name="username_plain",
    ),
    migrations.AddField(
        model_name="user",
        name="username_enc",
        field=EncryptedTextField(
            associated_data="username",
            null=True,
            verbose_name="username",
        ),
    ),
    migrations.AddField(
        model_name="user",
        name="username_hash",
        field=Sha256Field(
            null=True,
            unique=True,
            editable=False,
            max_length=64,
            verbose_name="username hash",
        ),
    ),
    # Email
    migrations.RenameField(
        model_name="user",
        old_name="email",
        new_name="email_plain",
    ),
    migrations.AddField(
        model_name="user",
        name="email_enc",
        field=EncryptedTextField(
            associated_data="email",
            null=True,
            verbose_name="email address",
        ),
    ),
    migrations.AddField(
        model_name="user",
        name="email_hash",
        field=Sha256Field(
            null=True,
            editable=False,
            max_length=64,
            verbose_name="email hash",
        ),
    ),
    # First name
    migrations.RenameField(
        model_name="user",
        old_name="first_name",
        new_name="first_name_plain",
    ),
    migrations.AddField(
        model_name="user",
        name="first_name_enc",
        field=EncryptedTextField(
            associated_data="first_name",
            null=True,
            verbose_name="first name",
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
    # Last name
    migrations.RenameField(
        model_name="user",
        old_name="last_name",
        new_name="last_name_plain",
    ),
    migrations.AddField(
        model_name="user",
        name="last_name_enc",
        field=EncryptedTextField(
            associated_data="last_name",
            null=True,
            verbose_name="last name",
        ),
    ),
]

class_migrations = [
    # Access code
    migrations.RenameField(
        model_name="class",
        old_name="access_code",
        new_name="access_code_plain",
    ),
    migrations.AddField(
        model_name="class",
        name="access_code_enc",
        field=EncryptedTextField(
            associated_data="access_code",
            null=True,
            verbose_name="access code",
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
    # Name
    migrations.RenameField(
        model_name="class",
        old_name="name",
        new_name="name_plain",
    ),
    migrations.AddField(
        model_name="class",
        name="name_enc",
        field=EncryptedTextField(
            associated_data="name",
            null=True,
            verbose_name="name",
        ),
    ),
]

school_teacher_invitation_migrations = [
    # Token
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="token",
        new_name="token_plain",
    ),
    migrations.AddField(
        model_name="schoolteacherinvitation",
        name="token_enc",
        field=EncryptedTextField(
            associated_data="token",
            null=True,
            verbose_name="token",
        ),
    ),
    migrations.AddField(
        model_name="schoolteacherinvitation",
        name="token_hash",
        field=Sha256Field(
            null=True,
            editable=False,
            max_length=64,
            verbose_name="token hash",
        ),
    ),
    # Invited teacher first name
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_first_name",
        new_name="invited_teacher_first_name_plain",
    ),
    migrations.AddField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_first_name_enc",
        field=EncryptedTextField(
            associated_data="invited_teacher_first_name",
            null=True,
            verbose_name="invited teacher first name",
        ),
    ),
    # Invited teacher last name
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_last_name",
        new_name="invited_teacher_last_name_plain",
    ),
    migrations.AddField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_last_name_enc",
        field=EncryptedTextField(
            associated_data="invited_teacher_last_name",
            null=True,
            verbose_name="invited teacher last name",
        ),
    ),
    # Invited teacher email
    migrations.RenameField(
        model_name="schoolteacherinvitation",
        old_name="invited_teacher_email",
        new_name="invited_teacher_email_plain",
    ),
    migrations.AddField(
        model_name="schoolteacherinvitation",
        name="invited_teacher_email_enc",
        field=EncryptedTextField(
            associated_data="invited_teacher_email",
            null=True,
            verbose_name="invited teacher email",
        ),
    ),
]

school_migrations = [
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
    # Name
    migrations.RenameField(
        model_name="school",
        old_name="name",
        new_name="name_plain",
    ),
    migrations.AddField(
        model_name="school",
        name="name_enc",
        field=EncryptedTextField(
            associated_data="name",
            null=True,
            verbose_name="name",
        ),
    ),
    # County
    migrations.RenameField(
        model_name="school",
        old_name="county",
        new_name="county_plain",
    ),
    migrations.AddField(
        model_name="school",
        name="county_enc",
        field=EncryptedTextField(
            associated_data="county",
            null=True,
            verbose_name="county",
        ),
    ),
]


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_user_proxies_and_new_models"),
    ]

    operations = [
        *user_migrations,
        *class_migrations,
        *school_teacher_invitation_migrations,
        *school_migrations,
    ]
