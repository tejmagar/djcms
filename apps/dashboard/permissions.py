"""
Permission level
Administrator > SEO > Editor > Author > Subscriber

Here role status can can do anything that lower level roles can do.
For example: Editor can do anything that author can do.
"""

from abc import ABC, abstractmethod
from typing import Union

from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse


class ViewPermissionMixin(ABC, AccessMixin):
    """
    Override allow_superuser if you don't want superuser to access the page
    """

    @abstractmethod
    def has_user_permission(self, request: HttpRequest) -> bool:
        pass

    def allow_superuser(self) -> bool:
        return True

    def _has_permission(self, request: HttpRequest) -> bool:
        if self.allow_superuser() and request.user.is_superuser:
            return True

        return self.has_user_permission(request)

    def dispatch(self, request, *args, **kwargs) -> Union[HttpResponseRedirect, HttpResponse]:
        if not self._has_permission(request):
            return HttpResponseRedirect(self.get_login_url())

        return super().dispatch(request, *args, **kwargs)


class SuperuserPermissionMixin(ViewPermissionMixin):
    """
    Only allow superuser to allow dashboard
    """

    def has_user_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser


class EditorMixin(ViewPermissionMixin):
    """
    Allow to access the page, if the current user role is editor.
    But, superuser also has access permission to the page.
    """

    def has_user_permission(self, request) -> bool:
        return request.user.role == get_user_model().Roles.EDITOR


class AuthorMixin(ViewPermissionMixin):
    """
    Allow to access the page, if the current user role is author.
    But, superuser also has access permission to the page.
    """

    allowed_roles = [get_user_model().Roles.EDITOR, get_user_model().Roles.AUTHOR]

    def has_user_permission(self, request: HttpRequest) -> bool:
        return request.user.role in self.allowed_roles
