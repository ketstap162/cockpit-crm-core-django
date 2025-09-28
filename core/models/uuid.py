from django.contrib.postgres.indexes import GistIndex


def get_uuid_index(model_name, fields: list[str] = None):
    if not fields:
        fields = ["uuid"]
    return GistIndex(fields=fields, name=f"idx_uuid_gist_{model_name}")
