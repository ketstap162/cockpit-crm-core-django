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
    list_display = (
        "display_name",
        "entity_type",
        "uuid",
        "is_current",
        "valid_from",
        "valid_to",
    )
    list_filter = ("entity_type", "is_current")
    search_fields = ("display_name", "uuid")
    ordering = ("display_name",)
    autocomplete_fields = ("entity_type",)
    readonly_fields = ("uuid", "valid_from", "valid_to")

    actions = ["close_selected"]

    def close_selected(self, request, queryset):
        """
        Closes the current version of the selected Entity.
        """
        for obj in queryset:
            obj.close()
        self.message_user(request, "Selected entities have been closed.")
    close_selected.short_description = "Close selected current versions"


@admin.register(models.EntityDetail)
class EntityDetailAdmin(SCD2ModelAdmin):
    form = EntityDetailForm

    list_display = (
        "entity_uuid",
        "detail_code",
        "value",
        "uuid",
        "is_current",
        "valid_from",
        "valid_to",
    )
    list_filter = ("is_current",)
    search_fields = ("detail_code", "value", "uuid")
    ordering = ("detail_code",)
    readonly_fields = ("uuid", "valid_from", "valid_to")
