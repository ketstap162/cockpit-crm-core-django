from typing import Any

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import F, Func, UniqueConstraint, Q


def get_no_overlap_versions(model_name: str, natural_key_fields: list[str] = None) -> ExclusionConstraint | None:
    if natural_key_fields:
        expressions: list[tuple[Any, Any]] = [(F(field), "=") for field in natural_key_fields]
        expressions.append((
            Func(
                F("valid_from"),
                Func(
                    F("valid_to"),
                    template="COALESCE(%(expressions)s, 'infinity')",
                    function="COALESCE"
                ),
                function="TSTZRANGE",
                template="TSTZRANGE(%(expressions)s, '[)')"
            ),
            RangeOperators.OVERLAPS
        ))

        return ExclusionConstraint(
            name=f"exclude_overlapping_{model_name}",
            expressions=expressions
        )
    return None


def get_unique_current_version(model_name: str, natural_key_fields: list[str] = None):
    if natural_key_fields:
        return UniqueConstraint(
            name=f"unique_current_version_{model_name}",
            fields=natural_key_fields,
            condition=Q(is_current=True),
        )
    return None


def get_scd2_constraint_list(model_name: str, natural_key_fields: list[str] = None):
    return [
        get_no_overlap_versions(model_name, natural_key_fields),
        get_unique_current_version(model_name, natural_key_fields),
    ]
