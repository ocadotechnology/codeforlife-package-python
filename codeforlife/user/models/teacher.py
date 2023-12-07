"""
© Ocado Group
Created on 05/12/2023 at 17:43:14(+00:00).

Teacher model.
"""

import typing as t

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from ...models import AbstractModel
from . import klass as _class
from . import school as _school
from . import school_teacher_invitation as _school_teacher_invitation
from . import user as _user


class Teacher(AbstractModel):
    """A user's teacher profile."""

    # pylint: disable-next=missing-class-docstring
    class Manager(AbstractModel.Manager):
        def create_user(self, teacher: t.Dict[str, t.Any], **fields):
            """Create a user with a teacher profile.

            Args:
                user: The user fields.

            Returns:
                A teacher profile.
            """

            return _user.User.objects.create_user(
                **fields,
                teacher=self.create(**teacher),
            )

    objects: Manager = Manager()

    user: "_user.User"
    classes: QuerySet["_class.Class"]
    school_invitations: QuerySet[
        "_school_teacher_invitation.SchoolTeacherInvitation"
    ]

    school: "_school.School" = models.ForeignKey(
        "user.School",
        related_name="teachers",
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
    )

    is_admin = models.BooleanField(
        _("is administrator"),
        default=False,
        help_text=_("Designates if the teacher has admin privileges."),
    )

    # TODO: add direct reference to students
