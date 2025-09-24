from django.contrib.postgres.constraints import ExclusionConstraint
from django.db.models import F, Func, UniqueConstraint, Q
from django.db import models
from django.utils import timezone

from core.models.uuid import UUIDMixin


class SCD2ConstraintCollection:
    scd2_constraint = ExclusionConstraint(
        name='no_overlap_entity_versions',
        expressions=[
            (F('uuid'), '='),
            (Func(F('valid_from'), F('valid_to'), function='tstzrange'), '&&')
        ],
    )
    unique_current_uuid = UniqueConstraint(
        fields=['uuid'],
        condition=Q(is_current=True),
        name='unique_current_uuid'
    )


class SCD2Mixin(UUIDMixin, models.Model):
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        abstract = True

        # Example: shows how to add SCD2-related constraints to the model
        constraints = [
            SCD2ConstraintCollection.scd2_constraint,
            SCD2ConstraintCollection.unique_current_uuid
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
        """
        Create a new version (new row).
        """
        self.close()
        attrs = {**self.__dict__, **kwargs}
        attrs.pop("id", None)  # Django will create a new PK
        attrs.pop("_state", None)  # Django internal state
        return self.__class__.objects.create(**attrs)
