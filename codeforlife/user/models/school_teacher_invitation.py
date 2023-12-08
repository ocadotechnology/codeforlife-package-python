# """
# © Ocado Group
# Created on 05/12/2023 at 17:44:14(+00:00).

# School teacher invitation model.
# """

# from datetime import timedelta

# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from ...models import AbstractModel
# from . import school as _school
# from . import teacher as _teacher


# def _set_expires_at():
#     return lambda: timezone.now() + timedelta(days=7)


# # TODO: move to portal
# class SchoolTeacherInvitation(AbstractModel):
#     """An invitation for a teacher to join a school."""

#     school: "_school.School" = models.ForeignKey(
#         "user.School",
#         related_name="teacher_invitations",
#         on_delete=models.CASCADE,
#     )

#     teacher: "_teacher.Teacher" = models.ForeignKey(
#         "user.Teacher",
#         related_name="school_invitations",
#         on_delete=models.CASCADE,
#     )

#     expires_at = models.DateTimeField(
#         _("is expired"),
#         default=_set_expires_at,
#         help_text=_("When the teacher was invited to the school."),
#     )

#     class Meta:
#         unique_together = ["school", "teacher"]

#     @property
#     def is_expired(self):
#         return self.expires_at < timezone.now()

#     def refresh(self):
#         self.expires_at = _set_expires_at()
#         self.save()
