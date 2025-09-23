from django.db import models
from core.models.uuid import UUIDMixin, btree_index_uuid
from core.models.scd2 import SCD2Mixin, SCD2ConstraintCollection


class EntityType(UUIDMixin, models.Model):
    # Fields
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Entity Type"
        verbose_name_plural = "Entity Types"
        indexes = [
            btree_index_uuid
        ]

    def __str__(self):
        return self.name


class Entity(SCD2Mixin, UUIDMixin, models.Model):
    # Fields
    display_name = models.CharField(max_length=255)

    # Keys
    entity_type = models.ForeignKey(EntityType, on_delete=models.PROTECT, related_name="entities")

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        indexes = [
            btree_index_uuid,
            models.Index(fields=['display_name']),
        ]
        constraints = [
            SCD2ConstraintCollection.scd2_constraint,
            SCD2ConstraintCollection.unique_current_uuid
        ]

    def __str__(self):
        return self.display_name
