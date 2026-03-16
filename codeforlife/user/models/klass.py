"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t
from datetime import timedelta
from uuid import uuid4

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...hashers import hash_credential
from ...models import EncryptedModel
from ...models.fields import EncryptedTextField
from ...types import Validators
from ...validators import (
    UnicodeAlphanumericCharSetValidator,
    UppercaseAsciiAlphanumericCharSetValidator,
)

if t.TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime

    from django_stubs_ext.db.models import TypedModelMeta

    from .student import Student
    from .teacher import SchoolTeacher, Teacher
else:
    TypedModelMeta = object


class_access_code_validators: Validators = [
    MinLengthValidator(5),
    MaxLengthValidator(5),
    UppercaseAsciiAlphanumericCharSetValidator(),
]

class_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-_",
    )
]


class ClassModelManager(EncryptedModel.Manager["Class"]):
    """Manager for Class model."""

    def get_original_queryset(self):
        """Get the original queryset without filtering."""
        return super().get_queryset()

    def get_queryset(self):
        """Filter out non active classes by default."""
        return super().get_queryset().filter(is_active=True)


# pylint: disable-next=too-many-instance-attributes
class Class(EncryptedModel):
    """A class."""

    students: QuerySet["Student"]

    associated_data = "class"

    # --------------------------------------------------------------------------
    # Name
    # --------------------------------------------------------------------------

    name_plain: str
    name_plain = models.CharField(max_length=200)  # type: ignore[assignment]
    name_enc = EncryptedTextField(
        associated_data="name",
        null=True,
        verbose_name=_("name"),
    )

    @property
    def name(self):
        """Get the name of the class."""
        if self.name_enc is not None:
            return self.name_enc
        return self.name_plain

    @name.setter
    def name(self, value: str):
        """Set the name of the class."""
        self.name_plain = value
        self.name_enc = value

    # --------------------------------------------------------------------------

    teacher: "SchoolTeacher"
    teacher = models.ForeignKey(  # type: ignore[assignment]
        "user.Teacher",
        related_name="class_teacher",
        on_delete=models.CASCADE,
    )

    # --------------------------------------------------------------------------
    # Access code
    # --------------------------------------------------------------------------

    access_code_hash = models.CharField(
        _("access code hash"), max_length=64, editable=False, null=True
    )
    access_code_plain: t.Optional[str]
    access_code_plain = models.CharField(  # type: ignore[assignment]
        max_length=5,
        null=True,
    )
    access_code_enc = EncryptedTextField(
        associated_data="access_code",
        null=True,
        verbose_name=_("access code"),
    )

    @property
    def access_code(self):
        """Get the access code for the class."""
        if self.access_code_enc is not None:
            return self.access_code_enc
        return self.access_code_plain

    @access_code.setter
    def access_code(self, value: t.Optional[str]):
        """Set the access code for the class."""
        self.access_code_plain = value
        self.access_code_enc = value
        self.access_code_hash = (
            value if value is None else hash_credential(value)
        )

    # --------------------------------------------------------------------------

    classmates_data_viewable: bool
    classmates_data_viewable = models.BooleanField(  # type: ignore[assignment]
        default=False
    )

    always_accept_requests: bool
    always_accept_requests = models.BooleanField(  # type: ignore[assignment]
        default=False
    )

    accept_requests_until: t.Optional["datetime"]
    accept_requests_until = models.DateTimeField(  # type: ignore[assignment]
        null=True
    )

    creation_time: t.Optional["datetime"]
    creation_time = models.DateTimeField(  # type: ignore[assignment]
        default=timezone.now, null=True
    )

    is_active: bool
    is_active = models.BooleanField(default=True)  # type: ignore[assignment]

    created_by: t.Optional["Teacher"]
    created_by = models.ForeignKey(  # type: ignore[assignment]
        "user.Teacher",
        null=True,
        blank=True,
        related_name="created_classes",
        on_delete=models.SET_NULL,
    )

    objects: ClassModelManager = ClassModelManager()  # type: ignore[assignment]

    def __str__(self):
        return self.name

    def has_students(self):
        """Check if the class has any students."""
        students = self.students.all()
        return students.count() != 0

    def get_requests_message(self):
        """Get the message regarding the class's request acceptance status."""
        if self.always_accept_requests:
            external_requests_message = (
                "This class is currently set to always accept requests."
            )
        elif (
            self.accept_requests_until is not None
            and (self.accept_requests_until - timezone.now()) >= timedelta()
        ):
            external_requests_message = (
                "This class is accepting external requests until "
                # pylint: disable-next=no-member
                + self.accept_requests_until.strftime("%d-%m-%Y %H:%M")
                + " "
                + timezone.get_current_timezone_name()
            )
        else:
            external_requests_message = (
                "This class is not currently accepting external requests."
            )

        return external_requests_message

    def anonymise(self):
        """Anonymise the class."""
        self.name = uuid4().hex
        self.access_code = ""
        self.is_active = False
        self.save()

        # Remove independent students' requests to join this class
        # pylint: disable-next=no-member
        self.class_request.clear()

    class Meta(TypedModelMeta):
        verbose_name_plural = "classes"

    @property
    def dek_aead(self):
        return self.teacher.school.dek_aead
