# from uuid import uuid4
# from datetime import timedelta

# from django.db import models
# from django.utils import timezone

# from .teacher import Teacher


# class ClassModelManager(models.Manager):
#     def all_members(self, user):
#         members = []
#         if hasattr(user, "teacher"):
#             members.append(user.teacher)
#             if user.teacher.has_school():
#                 classes = user.teacher.class_teacher.all()
#                 for c in classes:
#                     members.extend(c.students.all())
#         else:
#             c = user.student.class_field
#             members.append(c.teacher)
#             members.extend(c.students.all())
#         return members

#     # Filter out non active classes by default
#     def get_queryset(self):
#         return super().get_queryset().filter(is_active=True)


# class Class(models.Model):
#     name = models.CharField(max_length=200)
#     teacher = models.ForeignKey(
#         Teacher, related_name="class_teacher", on_delete=models.CASCADE
#     )
#     access_code = models.CharField(max_length=5, null=True)
#     classmates_data_viewable = models.BooleanField(default=False)
#     always_accept_requests = models.BooleanField(default=False)
#     accept_requests_until = models.DateTimeField(null=True)
#     creation_time = models.DateTimeField(default=timezone.now, null=True)
#     is_active = models.BooleanField(default=True)
#     created_by = models.ForeignKey(
#         Teacher,
#         null=True,
#         blank=True,
#         related_name="created_classes",
#         on_delete=models.SET_NULL,
#     )

#     objects = ClassModelManager()

#     def __str__(self):
#         return self.name

#     @property
#     def active_game(self):
#         games = self.game_set.filter(game_class=self, is_archived=False)
#         if len(games) >= 1:
#             assert (
#                 len(games) == 1
#             )  # there should NOT be more than one active game
#             return games[0]
#         return None

#     def has_students(self):
#         students = self.students.all()
#         return students.count() != 0

#     def get_requests_message(self):
#         if self.always_accept_requests:
#             external_requests_message = (
#                 "This class is currently set to always accept requests."
#             )
#         elif (
#             self.accept_requests_until is not None
#             and (self.accept_requests_until - timezone.now()) >= timedelta()
#         ):
#             external_requests_message = (
#                 "This class is accepting external requests until "
#                 + self.accept_requests_until.strftime("%d-%m-%Y %H:%M")
#                 + " "
#                 + timezone.get_current_timezone_name()
#             )
#         else:
#             external_requests_message = (
#                 "This class is not currently accepting external requests."
#             )

#         return external_requests_message

#     def anonymise(self):
#         self.name = uuid4().hex
#         self.access_code = ""
#         self.is_active = False
#         self.save()

#         # Remove independent students' requests to join this class
#         self.class_request.clear()

#     class Meta(object):
#         verbose_name_plural = "classes"

from common.models import Class
