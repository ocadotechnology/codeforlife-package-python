from django.db import models
from django.utils import timezone


class DailyActivity(models.Model):
    """
    A model to record sets of daily activity. Currently used to record the amount of
    student details download clicks, through the CSV and login cards methods, per day.
    """

    date = models.DateField(default=timezone.now)
    csv_click_count = models.PositiveIntegerField(default=0)
    login_cards_click_count = models.PositiveIntegerField(default=0)
    primary_coding_club_downloads = models.PositiveIntegerField(default=0)
    python_coding_club_downloads = models.PositiveIntegerField(default=0)
    level_control_submits = models.PositiveBigIntegerField(default=0)
    teacher_lockout_resets = models.PositiveIntegerField(default=0)
    indy_lockout_resets = models.PositiveIntegerField(default=0)
    school_student_lockout_resets = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Daily activities"

    def __str__(self):
        return f"Activity on {self.date}: CSV clicks: {self.csv_click_count}, login cards clicks: {self.login_cards_click_count}, primary pack downloads: {self.primary_coding_club_downloads}, python pack downloads: {self.python_coding_club_downloads}, level control submits: {self.level_control_submits}, teacher lockout resets: {self.teacher_lockout_resets}, indy lockout resets: {self.indy_lockout_resets}, school student lockout resets: {self.school_student_lockout_resets}"


# TODO: Do not use a Django model for this. Use CDN instead, where static files can be uploaded.
class DynamicElement(models.Model):
    """
    This model is meant to allow us to quickly update some elements dynamically on the website without having to
    redeploy everytime. For example, if a maintenance banner needs to be added, we check the box in the Django admin
    panel, edit the text and it'll show immediately on the website.
    """

    name = models.CharField(max_length=64, unique=True, editable=False)
    active = models.BooleanField(default=False)
    text = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
