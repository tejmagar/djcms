from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


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

    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # User role in DJ CMS
    role = models.CharField(max_length=60, choices=Roles.choices, null=True, blank=True)
    photo = models.ImageField(upload_to='uploads/', null=True, blank=True)

    @classmethod
    def login_with(cls) -> str:
        return cls.USERNAME_FIELD

    def __str__(self):
        return self.username


@receiver(pre_save, sender=User)
def update_role_status(sender: Any, instance: User, *args: Any, **kwargs: Any):
    if instance.is_superuser:
        instance.role = User.Roles.ADMINISTRATOR

    elif instance.role == User.Roles.ADMINISTRATOR:
        instance.is_staff = True
        instance.is_superuser = True

    else:
        instance.is_staff = False
        instance.is_superuser = False
