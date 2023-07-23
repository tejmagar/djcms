from typing import Type, Union

from django.db.models import Model


class UserQuery:
    """
    Use this class to query users with order and filters
    """

    def __init__(self, user_class: Type[Model]):
        self.user_class = user_class

    def get_queryset(self, order_by: Union[str, None] = None, role: Union[str, None] = None):
        return self.user_class.objects.filter(role=role).order_by(order_by)
