import uuid

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import UniqueConstraint, Q, Index, UUIDField

from core.models.base import BaseModel
from core.models.hashdiff.models import HashDiffMixin
from core.models.mixins import TimeStampMixin
from core.models.scd2.constraints import get_scd2_constraint_list
from core.models.scd2.models import SCD2BaseModel
from core.models.uuid import get_uuid_index
from entities.models_config import EntityConfig, EntityDetailConfig


class EntityType(TimeStampMixin, BaseModel):
    # Fields
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Entity Type"
        verbose_name_plural = "Entity Types"
        indexes = [
            get_uuid_index("entity_type")
        ]

    def __str__(self):
        return self.name


class Entity(TimeStampMixin, HashDiffMixin, SCD2BaseModel):
    # Fields
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
    display_name = models.CharField(max_length=255)

    # Keys
    entity_type = models.ForeignKey(
        EntityType,
        on_delete=models.PROTECT,
        related_name="entities",
        db_column="entity_type_id"
    )

    # Tech attributes (Not fields)
    scd2_config = EntityConfig.scd2
    hash_diff_config = EntityConfig.hash_diff

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        indexes = [
            get_uuid_index("entity"),
            GinIndex(fields=['display_name'], name='entity_display_name_gin', opclasses=['gin_trgm_ops'])
        ]
        constraints = [
            *get_scd2_constraint_list(
                EntityConfig.scd2.model_name,
                EntityConfig.scd2.natural_key_fields
            ),
        ]

    def __str__(self):
        return self.display_name


class EntityDetail(TimeStampMixin, HashDiffMixin, SCD2BaseModel):
    """
    Stores typed values for details associated with an Entity.
    Implements SCD2 in-table versioning.
    """
    # Fields
    detail_code = UUIDField(default=uuid.uuid4, editable=False, unique=False)
    value = models.TextField()  # store value as text, can normalize type in application

    # Keys
    entity_uuid = models.UUIDField()

    # Tech attributes (Not stored in DB)
    scd2_config = EntityDetailConfig.scd2
    hash_diff_config = EntityDetailConfig.hash_diff

    class Meta:
        verbose_name = "Entity Detail"
        verbose_name_plural = "Entity Details"
        indexes = [
            get_uuid_index("entity_detail", fields=["detail_code", "entity_uuid"]),
            Index(fields=['detail_code']),
        ]
        constraints = [
            *get_scd2_constraint_list(
                EntityDetailConfig.scd2.model_name,
                EntityDetailConfig.scd2.natural_key_fields
            ),
        ]
