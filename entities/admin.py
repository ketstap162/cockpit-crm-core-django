from django import forms
from django.contrib import admin

from core.models.base import BaseModelAdmin
from core.models.scd2.admin import SCD2ModelAdmin
from . import models
from .forms.admin import EntityDetailForm


@admin.register(models.EntityType)
class EntityTypeAdmin(BaseModelAdmin):
    list_display = ("code", "name", "uuid")
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("uuid",)


@admin.register(models.Entity)
class EntityAdmin(SCD2ModelAdmin):
    list_display = ("uuid", "entity_type", "display_name", "is_current", "valid_from", "valid_to",)
    list_filter = ("entity_type", "is_current")
    search_fields = ("display_name", "uuid")
    ordering = ("display_name",)
    autocomplete_fields = ("entity_type",)
    readonly_fields = ("uuid", "valid_from", "valid_to", "is_current", "hash_diff")


@admin.register(models.EntityDetail)
class EntityDetailAdmin(SCD2ModelAdmin):
    form = EntityDetailForm

    list_display = (
        "entity_uuid",
        "detail_code",
        "value",
        "is_current",
        "valid_from",
        "valid_to",
    )
    search_fields = ("detail_code", "entity_uuid")
    ordering = ("detail_code",)
    readonly_fields = ("detail_code", "valid_from", "valid_to", "is_current", "hash_diff")
