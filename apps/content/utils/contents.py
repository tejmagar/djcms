from typing import Type, Union

from django.db.models import Model, QuerySet
from django.contrib.auth import get_user_model


class ContentQuery:
    """
    Use this class for querying pages and posts
    """

    def __init__(self, model_class: Type[Model], user: get_user_model()):
        self.model_class = model_class
        self.user = user

    def get_all(self) -> QuerySet:
        """
        Returns all non trashed posts queryset
        """

        if self.user.is_superuser:
            return self.model_class.objects.filter(is_trash=False)

        return self.model_class.objects.filter(author=self.user, is_trash=False)

    def get_published(self) -> QuerySet:
        """
        Returns all posts queryset which is not draft and not trashed
        """

        if self.user.is_superuser:
            return self.model_class.objects.filter(is_trash=False, is_draft=False)

        return self.model_class.objects.filter(author=self.user, is_trash=False, is_draft=False)

    def get_draft(self) -> QuerySet:
        """
        Returns all draft post queryset which is not trashed
        """

        if self.user.is_superuser:
            return self.model_class.objects.filter(is_draft=True, is_trash=False)

        return self.model_class.objects.filter(author=self.user, is_draft=True, is_trash=False)

    def get_trash(self) -> QuerySet:
        """
        Returns all posts queryset with status is_trash=True
        """

        if self.user.is_superuser:
            return self.model_class.objects.filter(is_trash=True)

        return self.model_class.objects.filter(author=self.user, is_trash=True)

    def get_queryset(self, post_status: str) -> Union[QuerySet, None]:
        status_methods = {
            'all': self.get_all,
            'published': self.get_published,
            'draft': self.get_draft,
            'trash': self.get_trash
        }

        posts = status_methods.get(post_status, None)
        if posts:
            return posts()

        return None

    def posts_count_by_status(self) -> dict:
        """
        Returns only user owned posts count by status. If superuser, show all posts count.
        """

        queryset = self.model_class.objects

        if not self.user.is_superuser:
            queryset = queryset.filter(author=self.user)

        return {
            'all_posts_count': queryset.filter(is_trash=False).count(),
            'published_posts_count': queryset.filter(is_draft=False, is_trash=False).count(),
            'draft_posts_count': queryset.filter(is_draft=True, is_trash=False).count(),
            'trash_posts_count': queryset.filter(is_trash=True).count()
        }
