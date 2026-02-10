# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:49:56(+00:00).
"""

import typing as t

from django.db import models
from django.db.models import Q

from .school import School
from .user import User, UserProfile

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class TeacherModelManager(models.Manager):
    def factory(self, first_name, last_name, email, password):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user_profile = UserProfile.objects.create(user=user)

        return Teacher.objects.create(user=user_profile, new_user=user)

    def get_original_queryset(self):
        return super().get_queryset()

    # Filter out non active teachers by default
    def get_queryset(self):
        return super().get_queryset().filter(new_user__is_active=True)


class Teacher(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    new_user = models.OneToOneField(
        User,
        related_name="new_teacher",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    school = models.ForeignKey(
        School,
        related_name="teacher_school",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_admin = models.BooleanField(default=False)
    blocked_time = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        "self",
        related_name="invited_teachers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = TeacherModelManager()

    class Meta:
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
        if hasattr(userprofile, "student"):
            student = userprofile.student
            return (
                not student.is_independent()
                and student.class_field.teacher == self
            )

    def has_school(self):
        return self.school is not (None or "")

    def has_class(self):
        return self.class_teacher.exists()

    def __str__(self):
        return f"{self.new_user.first_name} {self.new_user.last_name}"


AnyTeacher = t.TypeVar("AnyTeacher", bound=Teacher)


class SchoolTeacher(Teacher):
    """A teacher that is in a school."""

    school: School

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=False)

    objects: models.Manager["SchoolTeacher"] = Manager()

    @property
    def student_users(self):
        """All student-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .user.student import StudentUser

        return StudentUser.objects.filter(
            **(
                {"new_student__class_field__teacher__school": self.school}
                if self.is_admin
                else {"new_student__class_field__teacher": self}
            )
        ).prefetch_related("new_student")

    @property
    def students(self):
        """All students the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .student import Student

        return Student.objects.filter(
            **(
                {"class_field__teacher__school": self.school}
                if self.is_admin
                else {"class_field__teacher": self}
            )
        ).prefetch_related("new_user")

    @property
    def classes(self):
        """All classes the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .klass import Class

        return Class.objects.filter(teacher__school=self.school)

    @property
    def indy_users(self):
        """All independent-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .user.independent import IndependentUser

        return IndependentUser.objects.filter(
            new_student__pending_class_request__in=self.classes
        )

    @property
    def school_teacher_users(self):
        """All school-teacher-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .user.school_teacher import SchoolTeacherUser

        return SchoolTeacherUser.objects.filter(new_teacher__school=self.school)

    @property
    def school_teachers(self):
        """All school-teachers the teacher can query."""
        return SchoolTeacher.objects.filter(school=self.school)

    @property
    def school_users(self):
        """All users in the school the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .user.user import User

        return User.objects.filter(
            Q(  # student-users
                new_teacher__isnull=True,
                **(
                    {"new_student__class_field__teacher__school": self.school}
                    if self.is_admin
                    else {"new_student__class_field__teacher": self}
                ),
            )
            | Q(  # school-teacher-users
                new_student__isnull=True,
                new_teacher__school=self.school,
            )
        )


class AdminSchoolTeacher(SchoolTeacher):
    """An admin-teacher that is in a school."""

    is_admin: t.Literal[True]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=True)

    objects: models.Manager["AdminSchoolTeacher"] = Manager()

    @property
    def is_last_admin(self):
        """Whether of not the teacher is the last admin in the school."""
        return (
            not self.__class__.objects.filter(school=self.school)
            .exclude(pk=self.pk)
            .exists()
        )


class NonAdminSchoolTeacher(SchoolTeacher):
    """A non-admin-teacher that is in a school."""

    is_admin: t.Literal[False]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=False)

    objects: models.Manager["NonAdminSchoolTeacher"] = Manager()


class NonSchoolTeacher(Teacher):
    """A teacher that is not in a school."""

    school: None
    is_admin: t.Literal[False]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=True)

    objects: models.Manager["NonSchoolTeacher"] = Manager()


# pylint: disable-next=invalid-name
TypedTeacher = t.Union[
    SchoolTeacher,
    AdminSchoolTeacher,
    NonAdminSchoolTeacher,
    NonSchoolTeacher,
]

AnyTypedTeacher = t.TypeVar("AnyTypedTeacher", bound=TypedTeacher)


# TODO: add this as a method on base Teacher model in new schema.
def teacher_as_type(
    teacher: Teacher, typed_teacher_class: t.Type[AnyTypedTeacher]
):
    """Convert a generic teacher to a typed teacher.

    Args:
        teacher: The teacher to convert.
        typed_teacher_class: The type of teacher to convert to.

    Returns:
        An instance of the typed teacher.
    """

    return typed_teacher_class(
        pk=teacher.pk,
        user=teacher.user,
        new_user=teacher.new_user,
        school=teacher.school,
        is_admin=teacher.is_admin,
        blocked_time=teacher.blocked_time,
        invited_by=teacher.invited_by,
    )
