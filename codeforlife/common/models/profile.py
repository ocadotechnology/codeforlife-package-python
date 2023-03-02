from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    developer = models.BooleanField(default=False)

    awaiting_email_verification = models.BooleanField(default=False)

    # Holds the user's earned kurono badges. This information has to be on the UserProfile as the Avatar objects are
    # deleted every time the Game gets deleted.
    # This is a string showing which badges in which worksheets have been earned. The format is "X:Y" where X is the
    # worksheet ID and Y is the badge ID. This repeats for all badges and each pair is comma-separated.
    aimmo_badges = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def joined_recently(self):
        now = timezone.now()
        return now - timedelta(days=7) <= self.user.date_joined


class EmailVerification(models.Model):
    user = models.ForeignKey(User, related_name="email_verifications", null=True, blank=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=30)
    email = models.CharField(max_length=200, null=True, default=None, blank=True)
    expiry = models.DateTimeField()
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Email verification for {self.user.username}, ({self.email})"
