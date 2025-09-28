from django.db import models
from django.utils import timezone


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=timezone.now, verbose_name="Updated at")

    class Meta:
        abstract = True
