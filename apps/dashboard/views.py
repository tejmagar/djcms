from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Type, Any, Union

from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import View, ListView
from django.db.models import QuerySet, Model
from django.http import Http404
from django.forms import ModelForm
from django.http.request import HttpRequest
from django.contrib.auth import get_user_model, login

from apps.content.models import Category, Post, Tag, Page, StatusMixin
from apps.content.utils.status import StatusAction
from apps.content.utils.contents import ContentQuery

from .forms import CategoryForm, PostForm, TagForm, PageForm, UserForm, AddUserForm
from .permissions import (
    SuperuserPermissionMixin,
    AuthorMixin
)


@dataclass
class AllContentViewContext:
    """
    Required key values for showing contents based on model class. eg: for Post/Page
    It is because, we reuse the same template file for displaying model contents
    """

    new_content_url: str
    edit_content_select: str
    reverse_content_edit_name: str


# Create your views here.

class DashboardView(SuperuserPermissionMixin, View):
    """
    Only allow superuser to view dashboard page
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'dashboard.html')


class AbstractAllContentView(AuthorMixin, ListView, ABC):
    """
    Show the content created by current author only but allow superuser to access all the specified content.
    Superuser can do all the CRUD operations.
    Generic ListView handles the pagination.
    """

    template_name: str = 'all-posts.html'
    title: str = 'Content'  # Default title to display in template
    model_class: Type[Model] = None
    content_query: ContentQuery = None

    paginate_by: int = 25
    all_posts_count: int = 0
    published_posts_count: int = 0
    draft_posts_count: int = 0

    def get_queryset(self) -> QuerySet:
        post_status: str = self.request.GET.get('post_status', 'all')
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        self.content_query: ContentQuery = ContentQuery(self.model_class, self.request.user)
        # Fetching role wise items from database
        queryset: QuerySet = self.content_query.get_queryset(post_status)
        if queryset is None:
            raise Http404()

        # Order is required for proper pagination
        return queryset.order_by('-pk')

    @abstractmethod
    def content_context(self) -> AllContentViewContext:
        """
        This is required to provide dynamic information of content.
        For example: url to create new content Post/Page
        """
        pass

    def render_to_response(self, context: Any, **response_kwargs: Any) -> TemplateResponse:
        content_context: AllContentViewContext = self.content_context()
        if not content_context:
            raise Exception('Please provide required navigation urls')

        # Merge content counts and other data to the context
        context = {
            **context,
            **self.content_query.posts_count_by_status(),
            **asdict(content_context),
            'title': self.title
        }
        return super().render_to_response(context, **response_kwargs)


class AllPostsView(AbstractAllContentView):
    """
    List all posts based on status.
    Listing logic is handled by AllContentView
    """

    model_class: Type[Model] = Post
    title: str = 'Posts'

    def content_context(self) -> AllContentViewContext:
        return AllContentViewContext(
            new_content_url=reverse('new_post'),
            edit_content_select=reverse('edit_post_select'),
            reverse_content_edit_name='edit_post'
        )


class AbstractAllPagesView(AbstractAllContentView):
    """
    List all pages based on status.
    Listing logic is handled by AllContentView
    """

    model_class: Type[Model] = Page
    title: str = 'Pages'

    def content_context(self) -> AllContentViewContext:
        return AllContentViewContext(
            new_content_url=reverse('new_page'),
            edit_content_select=reverse('edit_page_select'),
            reverse_content_edit_name='edit_page'
        )


class AbstractAddView(AuthorMixin, View, ABC):
    """
    Allow author and editor role to access the add post view.
    Superuser also has access permission to this page.
    """

    # For adding new post, we reuse the same 'edit-post.html'. So we pass the 'update_mode': False to context.
    # This helps the template to know we are adding new post.
    template_name: str = 'edit-post.html'
    title: str = 'Add'
    form: Type[ModelForm] = None
    redirect_success_url: str = None

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {
            'update_mode': False,
            'title': self.title
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        if not self.form:
            raise Exception('Please provide form class to validate input')

        form: ModelForm = self.form(data=request.POST)
        if form.is_valid():
            form.save()
            # To prevent form resubmit, redirect user to post editor area
            return redirect(self.redirect_success_url)

        return render(request, self.template_name, {
            'form': form,
            'update_mode': False,
            'title': self.title
        })


class AddPostView(AbstractAddView):
    form: Type[ModelForm] = PostForm
    redirect_success_url: str = reverse_lazy('edit_post_select')


class AddPageView(AbstractAddView):
    form: Type[ModelForm] = PageForm
    redirect_success_url: str = reverse_lazy('edit_page_select')


class AbstractEditContentView(AuthorMixin, View, ABC):
    """
    This view handles the post which is already saved in the database.
    Set 'update_mode': True, so that template knows we are editing the post.

    This view also handles actions like restore/trash/delete for specific instance
    """

    model_class: type[Model] = None
    edit_content_select_url: str = None
    # This path should accept the primary key argument
    edit_content_reverse_url_name: str = None

    def get_validated_instance(self, pk: int) -> StatusMixin:
        """
        Only allow to perform operations if the user has right else raise Http404 error
        Returns a model extending StatusMixin
        """

        if self.request.user.is_superuser:
            return get_object_or_404(self.model_class, pk=pk)

        return get_object_or_404(self.model_class, pk=pk, author=self.request.user)

    def get(self, request, **kwargs):
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        pk = kwargs.get('pk')

        # Any model class which extends StatusMixin can be used
        instance: StatusMixin = self.get_validated_instance(pk)
        form = PostForm(instance=instance)

        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': True
        })

    def post(self, request: HttpRequest, **kwargs):
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        pk: int = kwargs.get('pk')
        action_type: Union[str, None] = request.GET.get('action')

        # Any model class which extends StatusMixin can be used
        instance: StatusMixin = self.get_validated_instance(pk)

        # At first, check if there is any actions to perform like trash/restore/delete
        if action_type:
            # Let the custom StatusAction handle the operations
            action: StatusAction = StatusAction(instance)
            performed: bool = action.perform(action_type)

            if performed:
                return redirect(self.edit_content_select_url)

        # Continue editing post
        # Don't allow to edit trash post
        if instance.is_trash:
            raise Http404()

        form: ModelForm = PostForm(instance=instance, data=request.POST)

        if form.is_valid():
            form.save()

            # Prevent form resubmit by redirecting page
            return redirect(reverse(self.edit_content_reverse_url_name, kwargs={'pk': pk}))

        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': True
        })


class EditPostView(AbstractEditContentView):
    model_class: Type[Model] = Post
    edit_content_select_url: str = reverse_lazy('edit_post_select')
    edit_content_reverse_url_name: str = 'edit_post'


class EditPageView(AbstractEditContentView):
    model_class: Type[Model] = Page
    edit_content_select_url: str = reverse_lazy('edit_page_select')
    edit_content_reverse_url_name: str = 'edit_page'


class AbstractGroupView(AuthorMixin, View):
    """
    This is the abstract class for handling group items like Categories and Tags.
    """

    template_name: str = None
    form_class: Type[ModelForm] = None
    form_success_redirect_url: str = None
    model_class: Type[Model] = None

    def validate(self):
        if not self.template_name:
            raise Exception('Please provide a template name')

        if not self.form_class:
            raise Exception('Please provide compatible form class')

        if not self.form_success_redirect_url:
            raise Exception('Please provide a url to redirect after saving form')

    def get_items(self, order_by: str = '-pk') -> Union[QuerySet, None]:
        if not self.model_class:
            return None

        return self.model_class.objects.order_by(order_by).all()

    def get(self, request):
        self.validate()

        form: ModelForm = self.form_class()
        return render(request, self.template_name, {
            'form': form,
            'items': self.get_items()
        })

    def post(self, request):
        self.validate()

        form: ModelForm = self.form_class(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.form_success_redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'items': self.get_items()
        })


class CategoriesView(AbstractGroupView):
    template_name = 'categories.html'
    form_class = CategoryForm
    form_success_redirect_url = reverse_lazy('categories')
    model_class = Category


class AbstractEditGroupView(AuthorMixin, View):
    """
    Reusable class for Categories and Tags View
    """

    model_class: Type[Model]
    template_name = None
    form_class: Type[ModelForm] = None
    redirect_delete_url: str
    edit_category_url_name: str

    def validate(self):
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        if not self.template_name:
            raise Exception('Please provide template to use')

        if not self.form_class:
            raise Exception('Please provide form class')

        if not self.redirect_delete_url:
            raise Exception("Please provide a url to redirect after deletion")

        if not self.edit_category_url_name:
            raise Exception('Please provide a reverse url name to edit the instance')

    def get(self, request, **kwargs) -> HttpResponse:
        self.validate()

        pk: int = kwargs.get('pk')
        instance: Model = get_object_or_404(self.model_class, pk=pk)
        form: ModelForm = self.form_class(instance=instance)

        return render(request, self.template_name, {
            'form': form,
            'items': self.model_class.objects.all()
        })

    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        self.validate()

        pk: int = kwargs.get('pk')
        action_delete: Union[str, None] = request.POST.get('delete')
        instance: Model = get_object_or_404(self.model_class, pk=pk)

        # Handle delete action first
        if action_delete:
            instance.delete()
            return redirect(self.redirect_delete_url)

        # Handle update logic
        form: ModelForm = self.form_class(instance=instance, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse(self.edit_category_url_name, kwargs={'pk': instance.pk}))

        return render(request, self.template_name, {
            'form': form,
            'items': self.model_class.objects.all()
        })


class EditGroupView(AbstractEditGroupView):
    model_class = Category
    template_name = 'edit-category.html'
    form_class = CategoryForm
    redirect_delete_url = reverse_lazy('categories')
    edit_category_url_name = 'edit_category'


class TagsView(AbstractGroupView):
    template_name = 'tags.html'
    form_class = TagForm
    form_success_redirect_url = reverse_lazy('tags')
    model_class = Tag


class EditTagView(AbstractEditGroupView):
    model_class = Tag
    template_name = 'edit-tag.html'
    form_class = TagForm
    redirect_delete_url = reverse_lazy('tags')
    edit_category_url_name = 'edit_tag'


class MediaView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'media.html')


class AllUsers(SuperuserPermissionMixin, ListView):
    title: str = 'Users'
    template_name = 'all-users.html'
    queryset = get_user_model().objects.get_queryset()
    paginate_by = 50

    def get_extra_context(self) -> dict:
        return {
            'title': self.title,
            'all_users_count': get_user_model().objects.all().count(),
            'administrator_count': get_user_model().objects.filter(is_superuser=True, is_staff=True).count()
        }

    def render_to_response(self, context: Any, **response_kwargs: Any):
        context = {
            **self.get_extra_context(),
            **context
        }
        return super().render_to_response(context, **response_kwargs)


class AddUser(SuperuserPermissionMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form: ModelForm = AddUserForm()
        return render(request, 'add-user.html', {
            'form': form,
            'roles': get_user_model().Roles.choices
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        form: ModelForm = AddUserForm(data=request.POST)
        if form.is_valid():
            model: get_user_model() = form.save(commit=False)
            password: str = form.cleaned_data.get('password')
            model.set_password(password)
            model.save()
            return redirect(reverse('all_users'))

        return render(request, 'add-user.html', {
            'form': form,
            'roles': get_user_model().Roles.choices
        })


class EditUserView(SuperuserPermissionMixin, View):
    def get(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        pk: int = kwargs.get('pk')
        if pk:
            instance: get_user_model() = get_object_or_404(get_user_model(), pk=pk)
        else:
            instance = request.user

        form: ModelForm = UserForm(instance=instance)
        return render(request, 'edit-user.html', {
            'form': form,
            'roles': get_user_model().Roles.choices
        })

    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        pk: int = kwargs.get('pk')
        if pk:
            instance: get_user_model() = get_object_or_404(get_user_model(), pk=pk)
        else:
            instance = request.user

        form: ModelForm = UserForm(instance=instance, data=request.POST)
        if form.is_valid():
            model: get_user_model() = form.save(commit=False)

            password = form.cleaned_data.get('password')
            if password:
                model.set_password(password)

                # User is logout so login user
                login(request, model)

            model.save()
            return redirect(reverse('edit_user', kwargs={'pk': pk}) if pk else reverse('edit_profile'))

        print(form.errors)
        return render(request, 'edit-user.html', {
            'form': form,
            'roles': get_user_model().Roles.choices
        })
