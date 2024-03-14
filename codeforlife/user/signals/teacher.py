"""
© Ocado Group
Created on 14/03/2024 at 12:41:05(+00:00).
"""

from ...models.signals import model_receiver
from ..models import Teacher

teacher_receiver = model_receiver(Teacher)
