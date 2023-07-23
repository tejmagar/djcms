from typing import Union, Type

from django.http import HttpRequest
from django.db.models import QuerySet, Model


def order_queryset(request: HttpRequest, model_class: Type[Model], queryset: QuerySet) -> QuerySet:
    """
    Use this class to dynamically sort model from request.
    Pass the order_by and order in GET request.
    Default order is by 'pk'
    """

    order_by: Union[str, None] = request.GET.get('order_by')
    order: Union[str, None] = request.GET.get('order')
    order_by_value: str = 'pk'  # default order is by primary key

    # If there is no such field, return the original queryset
    if not (model_class and order_by and hasattr(model_class, order_by)):
        return queryset.order_by(order_by_value)

    if order_by:
        if order == 'DESC':
            order_by_value = f'-{order_by}'
        else:
            order_by_value = order_by

    return queryset.order_by(order_by_value)
