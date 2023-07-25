from typing import Optional, Type, List

from django.http import HttpRequest
from django.db.models import QuerySet, Model


def order_queryset(request: HttpRequest, model_class: Type[Model], queryset: QuerySet) -> QuerySet:
    """
    Use this class to dynamically sort model from request.
    Pass the order_by and order in GET request.
    Default order is by 'pk'
    """

    order_by: Optional[str] = request.GET.get('order_by')
    order: Optional[str] = request.GET.get('order')

    if not order_by:
        return queryset.order_by('pk')

    fields: List[str] = order_by.split(',')

    if len(fields) == 0:
        fields = ['pk']  # no order_by field is supplied, so create one with pk

    order_by_fields: List[str] = []

    # If there is no such field, return the original queryset
    for field in fields:
        field = field.strip()

        if not (model_class and field and hasattr(model_class, field)):
            return queryset.order_by('pk')  # Default order by

        if order_by:
            if order == 'DESC':
                order_by_fields.append(f'-{field}')
            else:
                order_by_fields.append(field)

    return queryset.order_by(*order_by_fields)
