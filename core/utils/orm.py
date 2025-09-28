from django.core.exceptions import MultipleObjectsReturned
from django.http import Http404
from rest_framework.exceptions import NotFound, ValidationError


def get_one_or_none(queryset, model_name=None, rest: bool = False):
    """
    Returns one object from the queryset or None.
    If there is more than one object, throws MultipleObjectsReturned.
    """
    items = list(queryset[:2])
    if not items:
        return None
    if len(items) > 1:
        if not model_name:
            model_name = queryset.model.__name__

        if rest:
            raise ValidationError(detail=f"Multiple objects of {model_name} found.")
        raise MultipleObjectsReturned(f"Expected at most one object of {model_name}, got {len(items)}.")

    return items[0]


def get_one_or_fail(queryset, message=None, rest: bool = False):
    """
    Returns one object or raises an appropriate exception.

    Parameters:
    - queryset: Django QuerySet
    - message: Custom message for exception
    - rest: If True, raises DRF NotFound, else Http404
    """

    model_name = queryset.model.__name__

    try:
        item = get_one_or_none(queryset, model_name=model_name)
        if item is None:
            if rest:
                raise NotFound(detail=message or f"{model_name} not found.")
            raise Http404(message or f"{model_name} not found.")
        return item

    except MultipleObjectsReturned as error:
        if rest:
            raise ValidationError(detail=message or f"Multiple objects of {model_name} found.")
        raise error
