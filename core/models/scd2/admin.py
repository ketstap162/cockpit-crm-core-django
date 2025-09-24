from core.models.base import BaseModelAdmin


class SCD2ModelAdmin(BaseModelAdmin):
    """
    A mixin for ModelAdmin with SCD2 support.
    Intercepts model updates and creates a new version instead of a direct update.
    """
    readonly_fields = ("uuid", "valid_from", "valid_to", "is_current")
    list_filter = ("is_current",)

    def save_model(self, request, obj, form, change):
        if change:
            obj.new_version(**form.cleaned_data)
        else:
            super().save_model(request, obj, form, change)
