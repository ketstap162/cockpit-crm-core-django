import uuid
from django.db import models
from django.contrib.postgres.indexes import GistIndex

from core.models.base import BaseModel


def get_uuid_indexes(model_name):
    return [
        GistIndex(fields=["uuid"], name=f"idx_uuid_gist_{model_name}")
    ]


class UUIDModel(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)

    class Meta:
        abstract = True

        # Example: demonstrates how to add an index to model
        # indexes = [btree_index_uuid]
        indexes = [
            *get_uuid_indexes("model_name")
        ]
