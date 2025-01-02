import uuid

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    class Meta:
        abstract = True
