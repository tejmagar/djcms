from django.db import models

from django.contrib.auth import get_user_model

from django_seo_plus.models import SeoMeta

from django.utils.text import slugify
from bs4 import BeautifulSoup


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(blank=True)
    parent_category = models.ForeignKey(to='Category', null=True, blank=True, on_delete=models.DO_NOTHING)
    description = models.TextField(null=True, blank=True)

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Post(SeoMeta):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(to=Category, blank=True)
    slug = models.SlugField(blank=True)
    is_draft = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_excerpt(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        text = soup.text
        return text[:300]

    def clean(self):
        if not self.excerpt:
            self.excerpt = f'{self.generate_excerpt().strip()}...'

        if not self.slug:
            self.slug = slugify(self.title)

    def __str__(self):
        return self.title


class Page(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(to=get_user_model(), null=True, blank=True, on_delete=models.DO_NOTHING)
    slug = models.SlugField(blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField(null=True, blank=True)

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    def __str__(self):
        return self.name
