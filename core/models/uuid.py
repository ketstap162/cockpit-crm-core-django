import uuid
from django.db import models
from django.contrib.postgres.indexes import BTreeIndex

btree_index_uuid = BTreeIndex(fields=["uuid"])


class UUIDMixin(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True

        # Example: demonstrates how to add an index to model
        indexes = [btree_index_uuid]
