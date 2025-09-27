from django.db import models
from django.contrib.admin import ModelAdmin


class BaseManager(models.Manager):
    def current(self):
        return self.filter(is_current=True)


class BaseModel(models.Model):
    objects = BaseManager()

    class Meta:
        abstract = True

    def check_fields_change(self, data: dict, set_attrs: bool = False) -> bool:
        """
        Check if any of the given fields have different values compared to the instance.

        Args:
            data (dict): dict of fields to check/update {field: value}.
            set_attrs (bool):
                - If False (default) — only checks, stops on the first difference found.
                - If True — updates all given fields on the instance and
                  returns True if at least one field changed.

        Returns:
            bool: True if at least one field value differs (or was updated), else False.
        """
        changed = False
        if set_attrs:
            for field, value in data.items():
                # track if any field actually changed
                if not changed and hasattr(self, field) and getattr(self, field) != value:
                    changed = True

                setattr(self, field, value)

        else:
            # only check, no modifications, exit early on first difference
            for field, value in data.items():
                if hasattr(self, field) and getattr(self, field) != value:
                    changed = True
                    break

        return changed


class BaseModelAdmin(ModelAdmin):
    pass
