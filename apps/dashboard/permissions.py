from abc import ABC, abstractmethod

from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth import get_user_model


class ViewPermissionMixin(ABC, AccessMixin):
    @abstractmethod
    def has_permission(self, request) -> bool:
        pass

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class SuperuserPermissionMixin(ViewPermissionMixin):
    """
    Only allow superuser to allow dashboard
    """

    def has_permission(self, request) -> bool:
        return request.user.is_superuser


class AuthorOrEditorMixin(ViewPermissionMixin):
    """
    Allow to access the page, if the current user is author or editor.
    But, superuser also has access permission to the page.
    """

    allowed_roles = [get_user_model().Roles.AUTHOR, get_user_model().Roles.EDITOR]

    def has_permission(self, request) -> bool:
        # Superuser can access author or editor contents
        if request.user.is_superuser:
            return True

        return request.user.is_authenticated and request.user.role in self.allowed_roles
