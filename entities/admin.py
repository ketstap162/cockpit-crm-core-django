from django.contrib import admin
from .models import EntityType, Entity


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "uuid")
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("uuid",)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
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
        Закриває поточну версію обраних Entity.
        """
        for obj in queryset:
            obj.close()
        self.message_user(request, "Selected entities have been closed.")
    close_selected.short_description = "Close selected current versions"
