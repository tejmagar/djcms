from typing import Type

from django import template
from django.http import HttpRequest

from ..permissions import (
    ViewPermissionMixin,
    AuthorMixin,
    EditorMixin,
    SuperuserPermissionMixin,
)

register = template.Library()

# Add submenus reverse url names here so that if the sub menu path is matched, parent is selected in the sidebar
sidebar_menus = {
    'dashboard': ['dashboard'],
    'posts': ['edit_post_select', 'new_post', 'categories', 'tags'],
    'media': ['media'],
    'pages': ['edit_page_select', 'new_page'],
    'users': ['all_users', 'edit_user', 'edit_profile', 'add_user']
}

sidebar_permissions: dict[str, Type[ViewPermissionMixin]] = {
    'dashboard': AuthorMixin,
    'posts': AuthorMixin,
    'media': AuthorMixin,
    'pages': EditorMixin,
    'users': AuthorMixin,
    'settings': SuperuserPermissionMixin
}


@register.simple_tag(takes_context=True)
def has_permission(context, menu_name: str) -> bool:
    request: HttpRequest = context.request

    mixin_class = sidebar_permissions.get(menu_name)
    if mixin_class:
        mixin = mixin_class()
        return mixin.has_permission(request)

    # None of the sidebar matched
    return False


@register.simple_tag(takes_context=True)
def should_expand_menu(context, menu_name) -> bool:
    """
    Parent reverse url name is passed from the template.
    Then we check if the parent menu has the current path reverse url name in sub menus.
    If it has, return True to expand the sidebar menu
    For example: {% should_expand_menu 'pages' as expand_page %}
    """

    reverse_url_name = context.request.resolver_match.url_name

    sub_menus = sidebar_menus.get(menu_name)

    if sub_menus:
        for sub_menu in sub_menus:
            if sub_menu == reverse_url_name:
                return True

    return False


@register.simple_tag(takes_context=True)
def current_url_name(context) -> bool:
    """
    Check if the given reverse url name resolves the current path
    """

    return context.request.resolver_match.url_name
