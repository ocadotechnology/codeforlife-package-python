from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.crypto import get_random_string

from ...models import BackupToken, User


class TestBackupToken(TestCase):
    def setUp(self):
        self.user = User.objects.get(id=2)

    def test_bulk_create(self):
        token = get_random_string(8)
        backup_tokens = BackupToken.objects.bulk_create(
            [BackupToken(user=self.user, token=token)]
        )

        assert check_password(token, backup_tokens[0].token)
        with self.assertRaises(ValidationError):
            BackupToken.objects.bulk_create(
                [
                    BackupToken(
                        user=self.user,
                        token=get_random_string(8),
                    )
                    for _ in range(BackupToken.max_count)
                ]
            )

    def test_create(self):
        token = get_random_string(8)
        backup_token = BackupToken.objects.create(user=self.user, token=token)

        assert check_password(token, backup_token.token)

        BackupToken.objects.bulk_create(
            [
                BackupToken(
                    user=self.user,
                    token=get_random_string(8),
                )
                for _ in range(BackupToken.max_count - 1)
            ]
        )

        with self.assertRaises(ValidationError):
            BackupToken.objects.create(
                user=self.user,
                token=get_random_string(8),
            )

    def test_check_token(self):
        token = get_random_string(8)
        backup_token = BackupToken.objects.create(user=self.user, token=token)

        assert backup_token.check_token(token)
        assert backup_token.id is None
        with self.assertRaises(BackupToken.DoesNotExist):
            BackupToken.objects.get(
                user=backup_token.user,
                token=backup_token.token,
            )
