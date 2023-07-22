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

        NONE = 'none'
        AUTHOR = 'author'
        EDITOR = 'editor'
        SEO = 'seo'
        ADMINISTRATOR = 'administrator'

    # User role in DJ CMS
    role = models.CharField(max_length=60, choices=Roles.choices, null=True, blank=True)
    photo = models.ImageField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.username

    def clean(self):
        """
        Update user roles
        """

        if self.role == self.Roles.ADMINISTRATOR:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
