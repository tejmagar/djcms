from django import forms

from apps.content.models import Category, Post, Page, Tag


class PostForm(forms.ModelForm):
    content = forms.CharField(required=False)

    class Meta:
        model = Post
        fields = ('title', 'content', 'meta_description', 'slug', 'is_draft')


class CategoryForm(forms.ModelForm):
    parent_category = forms.ModelChoiceField(queryset=Category.objects.get_queryset(), required=False)

    class Meta:
        model = Category
        fields = '__all__'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'


class PageForm(forms.ModelForm):
    content = forms.CharField(required=False)

    class Meta:
        model = Page
        fields = ('title', 'content', 'meta_description', 'slug', 'is_draft')
