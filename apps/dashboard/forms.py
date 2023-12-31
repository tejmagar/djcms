from abc import ABC

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ValidationError

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


class AbstractUserForm(forms.ModelForm):
    is_add_user = False
    role = forms.ChoiceField(required=False, choices=get_user_model().Roles.choices)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password = forms.CharField(required=is_add_user)
    confirm_password = forms.CharField(required=is_add_user)

    def clean_password(self) -> str:
        password = self.cleaned_data.get('password')
        if self.is_add_user and len(password.strip()) == 0:
            raise ValidationError('This field is required')

        return password

    def clean_confirm_password(self) -> str:
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if self.is_add_user and len(confirm_password.strip()) == 0:
            raise ValidationError('This field is required')

        if not password == confirm_password:
            raise ValidationError("Password don't match")

        return confirm_password

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'role', 'email')


class UserForm(AbstractUserForm):
    pass


class AddUserForm(AbstractUserForm):
    is_add_user = True

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'role', 'email')


class UserProfileForm(AbstractUserForm):
    role = None

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
