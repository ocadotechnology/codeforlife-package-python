from uuid import uuid4

from django.db import models
from django.utils import timezone

from .school import School
from .teacher import Teacher


class SchoolTeacherInvitationModelManager(models.Manager):
    # Filter out inactive invitations by default
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SchoolTeacherInvitation(models.Model):
    token = models.CharField(max_length=32)
    school = models.ForeignKey(School, related_name="teacher_invitations", null=True, on_delete=models.SET_NULL)
    from_teacher = models.ForeignKey(Teacher, related_name="school_invitations", null=True, on_delete=models.SET_NULL)
    creation_time = models.DateTimeField(default=timezone.now, null=True)
    is_active = models.BooleanField(default=True)

    objects = SchoolTeacherInvitationModelManager()

    @property
    def is_expired(self):
        return self.expiry < timezone.now()

    def __str__(self):
        return f"School teacher invitation for {self.invited_teacher_email} to {self.school.name}"

    def anonymise(self):
        self.invited_teacher_first_name = uuid4().hex
        self.invited_teacher_last_name = uuid4().hex
        self.invited_teacher_email = uuid4().hex
        self.is_active = False
        self.save()
