from core.models.base import BaseModelAdmin


class SCD2ModelAdmin(BaseModelAdmin):
    """
    A mixin for ModelAdmin with SCD2 support.
    Intercepts model updates and creates a new version instead of a direct update.
    """
    readonly_fields = ("valid_from", "valid_to", "is_current")
    list_filter = ("is_current", "valid_from", "valid_to")

    # scd_fields = ("valid_from", "valid_to", "is_current")

    actions = ["close_selected"]

    def close_selected(self, request, queryset):
        """
        Closes the current version of the selected Entity.
        """
        for obj in queryset:
            obj.close()
        self.message_user(request, "Selected entities have been closed.")
    close_selected.short_description = "Close selected current versions"
