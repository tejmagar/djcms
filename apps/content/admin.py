from django.contrib import admin

from .models import Category, Post, Page, Tag

# Register your models here.


admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Page)
admin.site.register(Tag)
