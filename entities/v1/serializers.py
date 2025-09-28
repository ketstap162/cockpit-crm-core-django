from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers

from core.utils.orm import get_one_or_none
from entities.models import Entity, EntityDetail
from entities.models import EntityType


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "id",
            "uuid",
            "display_name",
            "entity_type",
            "is_current",
        ]


class EntityDetailCreateSerializer(serializers.ModelSerializer):
    value = serializers.CharField()

    class Meta:
        model = EntityDetail
        fields = ["value"]


class EntityCreateSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(max_length=255)
    entity_type_code = serializers.CharField(max_length=50)
    detail = EntityDetailCreateSerializer(many=False, required=False)

    class Meta:
        model = Entity
        fields = ["display_name", "entity_type_code", "detail"]

    def validate_entity_type_code(self, value):  # noqa
        entity_types = EntityType.objects.filter(code=value)
        exception = serializers.ValidationError("Invalid entity_type_code")

        try:
            entity_type = get_one_or_none(entity_types)
        except MultipleObjectsReturned as e:
            raise exception

        if not entity_type:
            raise exception

        return entity_type


class EntityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityDetail
        fields = ["detail_code", "value"]


class EntityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityType
        fields = ["id", "code", "name"]


class EntitySnapshotSerializer(serializers.ModelSerializer):
    entity_type = EntityTypeSerializer(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "uuid",
            "display_name",
            "entity_type",
            "valid_from",
            "valid_to",
            "is_current",
        ]


class EntityHistorySerializer(serializers.ModelSerializer):
    entity_type = serializers.PrimaryKeyRelatedField(read_only=True)
    valid_from = serializers.DateTimeField(read_only=True)
    valid_to = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Entity
        fields = [
            "id",
            "uuid",
            "display_name",
            "entity_type",
            "valid_from",
            "valid_to",
            "is_current"
        ]


class EntityDetailHistorySerializer(serializers.ModelSerializer):
    valid_from = serializers.DateTimeField(read_only=True)
    valid_to = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EntityDetail
        fields = [
            "id",
            "detail_code",
            "value",
            "valid_from",
            "valid_to",
            "is_current"
        ]


class EntityDetailUpdateSerializer(serializers.ModelSerializer):
    value = serializers.CharField()

    class Meta:
        model = EntityDetail
        fields = ["value"]


class EntityUpdateSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(max_length=255, required=False)
    detail = EntityDetailUpdateSerializer(many=False, required=False)

    class Meta:
        model = Entity
        fields = ["display_name", "detail"]


class EntityAsOfSerializer(serializers.ModelSerializer):
    entities = EntityHistorySerializer(many=True)
    entity_details = EntityDetailHistorySerializer(many=True)
