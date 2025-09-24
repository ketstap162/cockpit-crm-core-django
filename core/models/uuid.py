import uuid
from django.db import models
from django.contrib.postgres.indexes import BTreeIndex

from core.models.base import BaseModel

btree_index_uuid = BTreeIndex(fields=["uuid"])


class UUIDMixin(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)

    class Meta:
        abstract = True

        # Example: demonstrates how to add an index to model
        indexes = [btree_index_uuid]
