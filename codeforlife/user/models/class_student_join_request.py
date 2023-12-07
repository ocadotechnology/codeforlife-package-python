# """
# © Ocado Group
# Created on 05/12/2023 at 17:46:22(+00:00).

# Class student join request model.
# """

# from django.db import models

# from ...models import AbstractModel
# from . import klass as _class
# from . import student as _student


# # TODO: move to portal
# class ClassStudentJoinRequest(AbstractModel):
#     """A request from a student to join a class."""

#     klass: "_class.Class" = models.ForeignKey(
#         "user.Class",
#         related_name="student_join_requests",
#         on_delete=models.CASCADE,
#     )

#     student: "_student.Student" = models.ForeignKey(
#         "user.Student",
#         related_name="class_join_requests",
#         on_delete=models.CASCADE,
#     )

#     # created_at = models.DateTimeField(
#     #     _("created at"),
#     #     auto_now_add=True,
#     #     help_text=_("When the teacher was invited to the school."),
#     # )

#     class Meta:
#         unique_together = ["klass", "student"]
#         # TODO: check student is independent
#         # assert class is receiving requests
