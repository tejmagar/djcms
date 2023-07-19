from typing import Type

import string
import random

from django.db.models import Model
from django.utils.text import slugify


def generate_unique_slug(model: Type[Model], title: str, suffix_length: int = 8, add_suffix: bool = False):
    """
    Always generates unique slug recursively
    """

    slug = slugify(title)

    # Add random suffixes to make unique slug
    if add_suffix:
        slug = ''.join(random.choices(string.ascii_lowercase + string.digits, k=suffix_length))

    # Check if there is already a record with same slug
    is_slug_unique = model.objects.filter(slug=slug).count() == 0
    if not is_slug_unique:
        # If there is post with same slug, generate new slug adding rando suffixes
        return generate_unique_slug(model, title, suffix_length, add_suffix=True)

    return slug
