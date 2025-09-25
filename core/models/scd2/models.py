from django.contrib.postgres.indexes import GistIndex
from django.db import models, transaction
from django.utils import timezone
import hashlib
from typing import Self

from core.models.base import BaseModel
from core.models.uuid import UUIDModel, get_uuid_indexes

from core.models.scd2.constraints import get_scd2_constraint_list


def get_scd2_indexes(model_name):
    return [
        *get_uuid_indexes(model_name),
        GistIndex(fields=["hash_diff"], name=f"idx_hd_gist_{model_name}")
    ]


class SCD2BaseModel(UUIDModel, BaseModel):
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    # change_ts = models.DateTimeField(default=timezone.now)
    hash_diff = models.CharField(max_length=64, blank=True, editable=False, db_index=False)

    # Tech attributes
    detection_fields = []

    class Meta:
        abstract = True

        # Example: shows how to add SCD2-related constraints to the model
        constraints = [
            *get_scd2_constraint_list("model_name"),
        ]
        indexes = [
            *get_scd2_indexes("model_name"),
        ]

    def get_hash_diff(self) -> str:
        values = [str(getattr(self, f)) for f in self.detection_fields]
        s = "|".join(values)
        return hashlib.sha256(s.encode()).hexdigest()

    def close(self, timestamp=None, save=False) -> Self:
        """
        Close the current version, set valid_to and is_current=False.
        """
        if self.is_current:
            self.is_current = False
            self.valid_to = timestamp or timezone.now()

            if save:
                self.save()

        return self

    def new_version(self, save=False, **kwargs) -> (Self, Self):
        timestamp = timezone.now()
        old_version = self.close(timestamp=timestamp)

        attrs = {**self.__dict__, **kwargs}
        attrs.pop("id", None)
        attrs.pop("_state", None)
        attrs["valid_from"] = timestamp
        attrs["valid_to"] = None
        attrs["is_current"] = True
        new_version = self.__class__(**attrs)

        if save:
            with transaction.atomic():
                old_version.save(update_fields=["valid_to", "is_current"])
                new_version.save()

        return new_version, old_version

    def inject(self, **kwargs):
        pass

    def save(self, *args, **kwargs):
        # Define hash_diff before saving
        self.hash_diff = self.get_hash_diff()
        super().save()
