"""
© Ocado Group
Created on 10/02/2026 at 14:00:56(+00:00).

Models that have been carried over from the old schema but are not yet fully
integrated into the new schema. These models are expected to be refactored and
integrated or removed in the new schema in the future.
"""

from django.db import models
from django.utils import timezone

from .klass import Class
from .school import School
from .student import Student
from .user import User


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    class_field = models.ForeignKey(Class, null=True, on_delete=models.SET_NULL)
    login_type = models.CharField(
        max_length=100, null=True
    )  # for student login

    def __str__(self):
        return f"{self.user} login: {self.login_time} type: {self.login_type}"


class JoinReleaseStudent(models.Model):
    """
    To keep track when a student is released to be independent student or
    joins a class to be a school student.
    """

    JOIN = "join"
    RELEASE = "release"

    student = models.ForeignKey(
        Student, related_name="student", on_delete=models.CASCADE
    )
    # either "release" or "join"
    action_type = models.CharField(max_length=64)
    action_time = models.DateTimeField(default=timezone.now)


class TotalActivity(models.Model):
    """
    A model to record total activity. Meant to only have one entry which
    records all total activity. An example of this is total ever registrations.
    """

    teacher_registrations = models.PositiveIntegerField(default=0)
    student_registrations = models.PositiveIntegerField(default=0)
    independent_registrations = models.PositiveIntegerField(default=0)
    anonymised_unverified_teachers = models.PositiveIntegerField(default=0)
    anonymised_unverified_independents = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Total activity"

    def __str__(self):
        return "Total activity"


class DailyActivity(models.Model):
    """
    A model to record sets of daily activity. Currently used to record the
    amount of student details download clicks, through the CSV and login
    cards methods, per day.
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
    anonymised_unverified_teachers = models.PositiveIntegerField(default=0)
    anonymised_unverified_independents = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Daily activities"

    def __str__(self):
        return f"Activity on {self.date}: CSV clicks: {self.csv_click_count}, login cards clicks: {self.login_cards_click_count}, primary pack downloads: {self.primary_coding_club_downloads}, python pack downloads: {self.python_coding_club_downloads}, level control submits: {self.level_control_submits}, teacher lockout resets: {self.teacher_lockout_resets}, indy lockout resets: {self.indy_lockout_resets}, school student lockout resets: {self.school_student_lockout_resets}, unverified teachers anonymised: {self.anonymised_unverified_teachers}, unverified independents anonymised: {self.anonymised_unverified_independents}"
