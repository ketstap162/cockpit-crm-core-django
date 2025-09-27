from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import F, Func, UniqueConstraint, Value, DateTimeField, Q, Index

from core.models.base import BaseModel
from core.models.uuid import UUIDModel, get_uuid_indexes
# from core.models.scd2 import SCD2Mixin, SCD2ConstraintCollection
from core.models.scd2.constraints import get_scd2_constraint_list
from core.models.scd2.models import SCD2BaseModel, get_scd2_indexes


class EntityType(UUIDModel, BaseModel):
    # Fields
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Entity Type"
        verbose_name_plural = "Entity Types"
        indexes = [
            *get_uuid_indexes("entity_type")
        ]

    def __str__(self):
        return self.name


class Entity(SCD2BaseModel):
    # Fields
    display_name = models.CharField(max_length=255)
    search_vector = SearchVectorField(null=True)

    # Keys
    entity_type = models.ForeignKey(
        EntityType,
        on_delete=models.PROTECT,
        related_name="entities",
        db_column="entity_type_id"
    )

    # Tech attributes (Not fields)
    detection_fields = ["display_name"]
    allow_hash_diff = False

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        indexes = [
            *get_scd2_indexes("entity"),
            GinIndex(fields=["search_vector"], name="entity_search_gin")
        ]
        constraints = [
            UniqueConstraint(
                fields=["uuid"],
                condition=Q(is_current=True),
                name="uniq_current_entity_per_uuid"
            ),
            ExclusionConstraint(
                name="exclude_overlapping_entity_versions",
                expressions=[
                    (F("uuid"), "="),
                    (
                        Func(
                            F("valid_from"),
                            Func(
                                F("valid_to"),
                                # Value("infinity", output_field=DateTimeField()),
                                template="COALESCE(%(expressions)s, 'infinity')",
                                function="COALESCE"
                            ),
                            function="TSTZRANGE"
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
            ),
            *get_scd2_constraint_list("entity"),
        ]

    def __str__(self):
        return self.display_name


class EntityDetail(SCD2BaseModel):
    """
    Stores typed values for details associated with an Entity.
    Implements SCD2 in-table versioning.
    """
    # Fields
    detail_code = models.CharField(max_length=100)
    value = models.TextField()  # store value as text, can normalize type in application

    # Keys
    entity_uuid = models.UUIDField()

    # Tech attributes
    detection_fields = ["detail_code", "value"]

    class Meta:
        verbose_name = "Entity Detail"
        verbose_name_plural = "Entity Details"
        indexes = [
            *get_scd2_indexes("entity_detail"),
            Index(fields=['detail_code']),
        ]
        constraints = [
            UniqueConstraint(
                fields=['entity_uuid', 'detail_code'],
                condition=models.Q(is_current=True),
                name='unique_current_entity_detail'
            ),
            UniqueConstraint(
                fields=['entity_uuid'],
                condition=models.Q(is_current=True),
                name='unique_current_per_entity_uuid'
            ),
            ExclusionConstraint(
                name="exclude_overlapping_entity_detail",
                expressions=[
                    (F("entity_uuid"), "="),
                    (F("detail_code"), "="),
                    (
                        Func(
                            F("valid_from"),
                            Func(
                                F("valid_to"),
                                template="COALESCE(%(expressions)s, 'infinity')",
                                function="COALESCE"), function="TSTZRANGE"
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
            ),
            *get_scd2_constraint_list("entity_detail"),
        ]
