from core.models.hashdiff.models import HashDiffConfig
from core.models.scd2.models import SCD2ModelConfig


class EntityConfig:
    scd2 = SCD2ModelConfig(
        model_name="entity",
        detection_fields=["display_name"],
        natural_key_fields=["uuid"],
    )
    hash_diff = HashDiffConfig(
        fields=["display_name", "is_current"]
    )


class EntityDetailConfig:
    scd2 = SCD2ModelConfig(
        model_name="entity_detail",
        detection_fields=["value"],
        natural_key_fields=["entity_uuid", "detail_code"]
    )
    hash_diff = HashDiffConfig(
        fields=["value", "is_current"]
    )
