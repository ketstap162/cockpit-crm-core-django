from django.contrib.postgres.indexes import GistIndex


def get_uuid_index(model_name, fields: list[str] = None):
    if not fields:
        fields = ["uuid"]
    return GistIndex(fields=fields, name=f"idx_uuid_gist_{model_name}")


# class UUIDModel(BaseModel):
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
#
#     class Meta:
#         abstract = True
#
#         # Example: demonstrates how to add an index to model
#         # indexes = [btree_index_uuid]
#         indexes = [
#             get_uuid_index("model_name")
#         ]
