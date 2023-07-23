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

    # Pass if you want a different url rather than current url user trying to access
    login_success_url: Union[str, None] = None

    @abstractmethod
    def has_user_permission(self, request: HttpRequest) -> bool:
        """
        This function is called only if the user is authenticated
        """

        pass

    def allow_superuser(self) -> bool:
        return True

    def has_permission(self, request: HttpRequest) -> bool:
        """
        This function will return True if the user is superuser. If you don't want that, use has_user_permission()
        """

        if self.allow_superuser() and request.user.is_superuser:
            return True

        return request.user.is_authenticated and self.has_user_permission(request)

    def dispatch(self, request, *args, **kwargs) -> Union[HttpResponseRedirect, HttpResponse]:
        if not self.has_permission(request):
            prepare_login_url = self.get_login_url()

            # Construct redirect urls
            if self.login_success_url:
                prepare_login_url += f'?next={self.login_success_url}'
            else:
                # Tell LoginView to redirect the same page after login successful
                prepare_login_url += f'?next={request.path}'

            return HttpResponseRedirect(prepare_login_url)

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
