from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    """
    We extend abstract user because in future we may need more fields to user tables.
    """

    class Roles(models.TextChoices):
        """
        DJ CMS gives user permissions to access views and perform operations based on these roles
        """

        AUTHOR = 'author'
        EDITOR = 'editor'

    # User role in DJ CMS
    role = models.CharField(max_length=60, choices=Roles.choices, null=True, blank=True)
