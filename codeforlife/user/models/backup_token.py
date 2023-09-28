import typing as t
from itertools import groupby

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from . import user


class BackupToken(models.Model):
    max_count = 10
    max_count_validation_error = ValidationError(
        f"Exceeded max count of {max_count}"
    )

    class Manager(models.Manager["BackupToken"]):
        def create(self, token: str, **kwargs):
            return super().create(token=make_password(token), **kwargs)

        def bulk_create(
            self,
            backup_tokens: t.List["BackupToken"],
            *args,
            **kwargs,
        ):
            def key(backup_token: BackupToken):
                return backup_token.user.id

            backup_tokens.sort(key=key)
            for user_id, group in groupby(backup_tokens, key=key):
                if (
                    len(list(group))
                    + BackupToken.objects.filter(user_id=user_id).count()
                    > BackupToken.max_count
                ):
                    raise BackupToken.max_count_validation_error

            for backup_token in backup_tokens:
                backup_token.token = make_password(backup_token.token)

            return super().bulk_create(backup_tokens, *args, **kwargs)

    objects: Manager = Manager()

    user: "user.User" = models.ForeignKey(
        "user.User",
        related_name="backup_tokens",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        max_length=8,
        validators=[MinLengthValidator(8)],
    )

    class Meta:
        unique_together = ["user", "token"]

    def save(self, *args, **kwargs):
        if self.id is None:
            if (
                BackupToken.objects.filter(user=self.user).count()
                >= BackupToken.max_count
            ):
                raise BackupToken.max_count_validation_error

        return super().save(*args, **kwargs)

    def check_token(self, token: str):
        if check_password(token, self.token):
            self.delete()
            return True
        return False
