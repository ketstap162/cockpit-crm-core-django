from django.contrib.postgres.constraints import ExclusionConstraint
from django.db.models import F, Func, UniqueConstraint, Q


def get_no_overlap_versions(model_name: str):
    return ExclusionConstraint(
        name=f"no_overlap_versions_{model_name}",
        expressions=[
            (F('uuid'), '='),
            (Func(F('valid_from'), F('valid_to'), function='tstzrange'), '&&')
        ],
    )


def get_unique_current_uuid(model_name: str):
    return UniqueConstraint(
        name=f"unique_current_uuid_{model_name}",
        fields=['uuid'],
        condition=Q(is_current=True),
    )


def get_scd2_constraint_list(model_name: str):
    return [
        get_no_overlap_versions(model_name),
        get_unique_current_uuid(model_name)
    ]
