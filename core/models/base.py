from django.db import models
from django.contrib.admin import ModelAdmin


class BaseManager(models.Manager):
    def current(self):
        return self.filter(is_current=True)


class BaseModel(models.Model):
    objects = BaseManager()

    class Meta:
        abstract = True


class BaseModelAdmin(ModelAdmin):
    pass
