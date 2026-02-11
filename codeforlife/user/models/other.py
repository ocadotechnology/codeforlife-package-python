"""
© Ocado Group
Created on 10/02/2026 at 14:00:56(+00:00).

Models that have been carried over from the old schema but are not yet fully
integrated into the new schema. These models are expected to be refactored and
integrated or removed in the new schema in the future.
"""

import typing as t

from django.db import models
from django.utils import timezone

if t.TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime

    from django_stubs_ext.db.models import TypedModelMeta

    from .klass import Class
    from .school import School
    from .student import Student
    from .user import User
else:
    TypedModelMeta = object


class UserSession(models.Model):
    """A model to track user sessions."""

    user: "User"
    user = models.ForeignKey(  # type: ignore[assignment]
        "user.User",
        on_delete=models.CASCADE,
    )

    login_time: "datetime"
    login_time = models.DateTimeField(  # type: ignore[assignment]
        default=timezone.now
    )

    school: t.Optional["School"]
    school = models.ForeignKey(  # type: ignore[assignment]
        "user.School",
        null=True,
        on_delete=models.SET_NULL,
    )

    class_field: t.Optional["Class"]
    class_field = models.ForeignKey(  # type: ignore[assignment]
        "user.Class",
        null=True,
        on_delete=models.SET_NULL,
    )

    # for student login
    login_type: t.Optional[str]
    login_type = models.CharField(  # type: ignore[assignment]
        max_length=100,
        null=True,
    )

    def __str__(self):
        return f"{self.user} login: {self.login_time} type: {self.login_type}"


class JoinReleaseStudent(models.Model):
    """
    To keep track when a student is released to be independent student or
    joins a class to be a school student.
    """

    JOIN = "join"
    RELEASE = "release"

    student: "Student"
    student = models.ForeignKey(  # type: ignore[assignment]
        "user.Student",
        related_name="student",
        on_delete=models.CASCADE,
    )

    # either "release" or "join"
    action_type: str
    action_type = models.CharField(max_length=64)  # type: ignore[assignment]

    action_time: "datetime"
    action_time = models.DateTimeField(  # type: ignore[assignment]
        default=timezone.now
    )


class TotalActivity(models.Model):
    """
    A model to record total activity. Meant to only have one entry which
    records all total activity. An example of this is total ever registrations.
    """

    teacher_registrations: int
    teacher_registrations = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    student_registrations: int
    student_registrations = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    independent_registrations: int
    independent_registrations = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    anonymised_unverified_teachers: int
    anonymised_unverified_teachers = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    anonymised_unverified_independents: int
    anonymised_unverified_independents = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        verbose_name_plural = "Total activity"

    def __str__(self):
        return "Total activity"


class DailyActivity(models.Model):
    """
    A model to record sets of daily activity. Currently used to record the
    amount of student details download clicks, through the CSV and login
    cards methods, per day.
    """

    date: "datetime"
    date = models.DateField(default=timezone.now)  # type: ignore[assignment]

    csv_click_count: int
    csv_click_count = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    login_cards_click_count: int
    login_cards_click_count = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    primary_coding_club_downloads: int
    primary_coding_club_downloads = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    python_coding_club_downloads: int
    python_coding_club_downloads = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    level_control_submits: int
    level_control_submits = models.PositiveBigIntegerField(
        default=0
    )  # type: ignore[assignment]

    teacher_lockout_resets: int
    teacher_lockout_resets = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    indy_lockout_resets: int
    indy_lockout_resets = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    school_student_lockout_resets: int
    school_student_lockout_resets = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    anonymised_unverified_teachers: int
    anonymised_unverified_teachers = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    anonymised_unverified_independents: int
    anonymised_unverified_independents = models.PositiveIntegerField(
        default=0
    )  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        verbose_name_plural = "Daily activities"

    def __str__(self):
        # pylint: disable-next=line-too-long
        return f"Activity on {self.date}: CSV clicks: {self.csv_click_count}, login cards clicks: {self.login_cards_click_count}, primary pack downloads: {self.primary_coding_club_downloads}, python pack downloads: {self.python_coding_club_downloads}, level control submits: {self.level_control_submits}, teacher lockout resets: {self.teacher_lockout_resets}, indy lockout resets: {self.indy_lockout_resets}, school student lockout resets: {self.school_student_lockout_resets}, unverified teachers anonymised: {self.anonymised_unverified_teachers}, unverified independents anonymised: {self.anonymised_unverified_independents}"
