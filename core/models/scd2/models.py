from typing import Self

from django.db import models, transaction
from django.utils import timezone

from core.models.base import BaseModel
from core.models.scd2.constraints import get_scd2_constraint_list


class SCD2ModelConfig:
    detection_fields: list[str] = []

    def __init__(
            self,
            model_name: str = None,
            detection_fields: list[str] = None,
            natural_key_fields: list[str] = None
    ):
        self.model_name = model_name
        self.detection_fields = detection_fields
        self.natural_key_fields = natural_key_fields


class SCD2BaseModel(BaseModel):
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    # Tech attributes (Not stored in DB)
    scd2_config: SCD2ModelConfig

    class Meta:
        abstract = True

        # Example: shows how to add SCD2-related constraints to the model
        constraints = [
            *get_scd2_constraint_list("model_name"),
        ]

    def close(self, timestamp=None, save=False) -> Self:
        """
        Close the current version, set valid_to and is_current=False.
        """
        if self.is_current:
            self.is_current = False
            self.valid_to = timestamp or timezone.now()

            if save:
                self.save(new_version=False)

        return self

    def new_version(self, save=True, with_transaction=True, *args, **kwargs) -> (Self, Self):
        timestamp = timezone.now()

        old_version = self.__class__.objects.get(pk=self.pk)
        old_version = old_version.close(timestamp=timestamp)

        attrs = {**self.__dict__, **kwargs}
        attrs.pop("id", None)
        attrs.pop("_state", None)
        attrs["valid_from"] = timestamp
        attrs["valid_to"] = None
        attrs["is_current"] = True
        new_version = self.__class__(**attrs)

        if save:
            if with_transaction:
                with transaction.atomic():
                    old_version.save(
                        new_version=False,
                        update_fields=["valid_to", "is_current"]
                    )
                    new_version.save(new_version=False)
            else:
                old_version.save(
                    new_version=False,
                    update_fields=["valid_to", "is_current"]
                )
                new_version.save(new_version=False)

        return new_version, old_version

    def _has_changes(self):
        """
        Check if any of the detection_fields have changed compared to the current DB version.
        """
        if not self.pk or not self.scd2_config.detection_fields:
            return True  # new object or no detection fields → consider as changed

        db_obj = self.__class__.objects.filter(pk=self.pk).first()
        if not db_obj:
            return True

        for field in self.scd2_config.detection_fields:
            if getattr(self, field) != getattr(db_obj, field):
                return True

        return False

    def save(self, new_version=True, with_transaction=False, *args, **kwargs):
        if self.pk and new_version and self._has_changes():
            return self.new_version(save=True, with_transaction=with_transaction, *args, **kwargs)
        super().save(*args, **kwargs)
