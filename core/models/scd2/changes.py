from datetime import datetime
from typing import Any

from django.db.models import QuerySet

from core.models.scd2.models import SCD2BaseModel


def get_object_changes(
        new_version: SCD2BaseModel,
        old_version: SCD2BaseModel
) -> (list[dict], datetime):
    if type(new_version) is not type(old_version):
        raise TypeError(
            f"Objects must be of the same class, got {type(new_version).__name__} and {type(old_version).__name__}"
        )

    if new_version.valid_from != old_version.valid_to:
        raise ValueError(
            f"Invalid version transition: "
            f"{type(new_version).__name__} new_version.valid_from={new_version.valid_from} "
            f"does not match old_version.valid_to={old_version.valid_to}"
        )

    changes = []

    for field in new_version.detection_fields:
        new_value = getattr(new_version, field)
        old_value = getattr(old_version, field)

        if new_value != old_value:
            changes.append(
                {
                    field: {
                        "old_value": old_value,
                        "new_value": new_value,
                    }
                }
            )

    return changes, new_version.valid_from


def get_changes_all(queryset: QuerySet[SCD2BaseModel] | list[SCD2BaseModel]) -> dict | None:
    queryset_len = len(queryset)
    if queryset_len < 2:
        return None

    total_changes = {}
    for index in range(0, queryset_len - 1):
        changes, change_dt = get_object_changes(queryset[index], queryset[index + 1])
        change_dt_str = str(change_dt)

        if change_dt_str not in changes:
            total_changes[str(change_dt_str)] = changes
        else:
            total_changes[str(change_dt_str)] += changes

    return total_changes


def map_by_field(collection: QuerySet | list, field_name: str) -> dict:
    result = {}

    for obj in collection:
        key = str(getattr(obj, field_name))

        if key not in result:
            result[key] = [obj]
        else:
            result[key].append(obj)

    return result


def fill_dict_with_changes(
        changes_dict: dict,
        collection_by_key: dict[str, Any],
        second_key_name: str,
) -> None:
    for key, item_list in collection_by_key.items():
        changes: dict = get_changes_all(item_list)

        if not changes:
            continue

        if key not in changes_dict:
            changes_dict[key] = {
                second_key_name: changes
            }
        else:
            if second_key_name not in changes_dict[key].keys():
                changes_dict[key][second_key_name] = changes
            else:
                changes_dict[key][second_key_name].extend(changes)
