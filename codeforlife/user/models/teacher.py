# from django.db import models

# from .user import User
# from .school import School


# class TeacherModelManager(models.Manager):
#     def factory(self, first_name, last_name, email, password):
#         user = User.objects.create_user(
#             username=email,
#             email=email,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#         )

#         return Teacher.objects.create(user=user)

#     # Filter out non active teachers by default
#     def get_queryset(self):
#         return super().get_queryset().filter(user__is_active=True)


# class Teacher(models.Model):
#     user = models.OneToOneField(
#         User,
#         related_name="teacher",
#         null=True,
#         blank=True,
#         on_delete=models.CASCADE,
#     )
#     school = models.ForeignKey(
#         School,
#         related_name="school_teacher",
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#     )
#     is_admin = models.BooleanField(default=False)
#     blocked_time = models.DateTimeField(null=True, blank=True)
#     invited_by = models.ForeignKey(
#         "self",
#         related_name="invited_teachers",
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#     )

#     objects = TeacherModelManager()

#     def teaches(self, userprofile):
#         if hasattr(userprofile, "student"):
#             student = userprofile.student
#             return (
#                 not student.is_independent()
#                 and student.class_field.teacher == self
#             )

#     def has_school(self):
#         return self.school is not (None or "")

#     def has_class(self):
#         return self.class_teacher.exists()

#     def __str__(self):
#         return f"{self.user.first_name} {self.user.last_name}"

from common.models import Teacher
