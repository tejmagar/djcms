from typing import List

from django import template

register = template.Library()

# Key is sidebar name and values are actual url names defined in paths
sidebar_menus = {
    'dashboard': ['dashboard'],
    'posts': ['edit_post_select', 'new_post', 'categories', 'tags'],
    'media': ['media']
}


@register.simple_tag(takes_context=True)
def should_expand_menu(context, menu_name):
    current_url_name = context.request.resolver_match.url_name
    sub_menus = sidebar_menus.get(menu_name)

    if sub_menus:
        for sub_menu in sub_menus:
            if sub_menu == current_url_name:
                return True

    return False
