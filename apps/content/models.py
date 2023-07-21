from bs4 import BeautifulSoup

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django_seo_plus.models import SeoMeta

from apps.content.utils.slugify import generate_unique_slug


# Create your models here.


class StatusMixin(models.Model):
    is_draft = models.BooleanField(default=True)
    is_trash = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Post(SeoMeta, StatusMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(to='Category', blank=True)
    slug = models.SlugField(blank=True, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        # Generate short page description for post index page
        if not self.excerpt:
            self.excerpt = f'{self.generate_excerpt().strip()}...'

        # Generate unique slugs
        if not self.slug:
            self.slug = generate_unique_slug(Post, self.title)

    def generate_excerpt(self) -> str:
        soup = BeautifulSoup(self.content, 'html.parser')
        text = soup.text
        return text[:300]


class Page(SeoMeta, StatusMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(to=get_user_model(), null=True, blank=True, on_delete=models.DO_NOTHING)
    slug = models.SlugField(blank=True, unique=True)

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if not self.slug:
            self.slug = generate_unique_slug(Page, self.title)


class Category(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(blank=True, unique=True)
    parent_category = models.ForeignKey(to='Category', null=True, blank=True, on_delete=models.DO_NOTHING)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)
