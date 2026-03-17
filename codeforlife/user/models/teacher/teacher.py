"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t

from django.db import models

if t.TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime

    from django_stubs_ext.db.models import TypedModelMeta

    from ..school import School
    from ..user import User, UserProfile
else:
    TypedModelMeta = object


class TeacherModelManager(models.Manager):
    """Manager for Teacher model."""

    def factory(self, first_name, last_name, email, password):
        """
        Factory method to create a new teacher with an associated user and user
        profile.
        """
        # NOTE: avoid circular imports by importing here
        # pylint: disable-next=import-outside-toplevel
        from ..user import User, UserProfile

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user_profile = UserProfile.objects.create(user=user)

        return Teacher.objects.create(user=user_profile, new_user=user)

    def get_original_queryset(self):
        """Get the original queryset without filtering."""
        return super().get_queryset()

    # Filter out non active teachers by default
    def get_queryset(self):
        """Filter out non active teachers by default."""
        return super().get_queryset().filter(new_user__is_active=True)


class Teacher(models.Model):
    """A teacher."""

    user: "UserProfile"
    user = models.OneToOneField(  # type: ignore[assignment]
        "user.UserProfile",
        on_delete=models.CASCADE,
    )

    new_user: t.Optional["User"]
    new_user = models.OneToOneField(  # type: ignore[assignment]
        "user.User",
        related_name="new_teacher",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    school: t.Optional["School"]
    school = models.ForeignKey(  # type: ignore[assignment]
        "user.School",
        related_name="teacher_school",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    is_admin: bool
    is_admin = models.BooleanField(default=False)  # type: ignore[assignment]

    blocked_time: t.Optional["datetime"]
    blocked_time = models.DateTimeField(  # type: ignore[assignment]
        null=True,
        blank=True,
    )

    invited_by: t.Optional["Teacher"]
    invited_by = models.ForeignKey(  # type: ignore[assignment]
        "self",
        related_name="invited_teachers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = TeacherModelManager()

    class Meta(TypedModelMeta):
        constraints = [
            models.CheckConstraint(
                check=~models.Q(
                    school__isnull=True,
                    is_admin=True,
                ),
                name="teacher__is_admin",
            )
        ]

    def teaches(self, userprofile):
        """Check if the teacher teaches the given userprofile."""
        if hasattr(userprofile, "student"):
            student = userprofile.student
            return (
                not student.is_independent()
                and student.class_field.teacher == self
            )

        return False

    def has_school(self):
        """Check if the teacher has an associated school."""
        return self.school is not (None or "")

    def has_class(self):
        """Check if the teacher has an associated class."""
        return self.class_teacher.exists()

    def __str__(self):
        if self.new_user is None:
            return super().__str__()

        return f"{self.new_user.first_name} {self.new_user.last_name}"


AnyTeacher = t.TypeVar("AnyTeacher", bound=Teacher)
