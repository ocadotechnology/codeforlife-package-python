"""
© Ocado Group
Created on 05/12/2023 at 17:44:14(+00:00).

School teacher invitation model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...models import AbstractModel
from . import school as _school
from . import teacher as _teacher


class SchoolTeacherInvitation(AbstractModel):
    """An invitation for a teacher to join a school."""

    school: "_school.School" = models.ForeignKey(
        "user.School",
        related_name="teacher_invitations",
        on_delete=models.CASCADE,
    )

    teacher: "_teacher.Teacher" = models.ForeignKey(
        "user.Teacher",
        related_name="school_invitations",
        on_delete=models.CASCADE,
    )

    # created_at = models.DateTimeField(
    #     _("created at"),
    #     auto_now_add=True,
    #     help_text=_("When the teacher was invited to the school."),
    # )

    # expires_at = models.DateTimeField()

    class Meta:
        unique_together = ["school", "teacher"]

    # @property
    # def is_expired(self):
    #     return self.expires_at < timezone.now()
