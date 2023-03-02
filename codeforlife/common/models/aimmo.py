from django.db import models


# TODO: this should not be here! move to aimmo repo.


class AimmoCharacterManager(models.Manager):
    def sorted(self):
        return self.get_queryset().order_by("sort_order")


class AimmoCharacter(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_path = models.CharField(max_length=255)
    sort_order = models.IntegerField()
    alt = models.CharField(max_length=255, null=True)
    objects = AimmoCharacterManager()

    def __str__(self) -> str:
        return self.name
