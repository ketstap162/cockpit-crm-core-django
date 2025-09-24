from django.db import models
from django.utils import timezone

from core.models.base import BaseModel
from core.models.uuid import UUIDMixin

from core.models.scd2.constraints import get_scd2_constraint_list


class SCD2BaseModel(UUIDMixin, BaseModel):
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        abstract = True

        # Example: shows how to add SCD2-related constraints to the model
        constraints = [
            *get_scd2_constraint_list("model_name"),
        ]

    def close(self, timestamp=None):
        """
        Close the current version, set valid_to and is_current=False.
        """
        if self.is_current:
            self.is_current = False
            self.valid_to = timestamp or timezone.now()
            self.save(update_fields=['is_current', 'valid_to'])

    def new_version(self, **kwargs):
        timestamp = timezone.now()
        self.close(timestamp)
        attrs = {**self.__dict__, **kwargs}
        attrs.pop("id", None)
        attrs.pop("_state", None)
        attrs["valid_from"] = timestamp
        attrs["valid_to"] = None
        attrs["is_current"] = True
        return self.__class__.objects.create(**attrs)
