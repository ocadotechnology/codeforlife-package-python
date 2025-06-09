"""
© Ocado Group
Created on 14/03/2024 at 12:52:50(+00:00).

Helpers for module "django.db.models.signals".
https://docs.djangoproject.com/en/5.1/ref/signals/#module-django.db.models.signals
"""

from .general import UpdateFields, update_fields_includes
from .receiver import model_receiver
