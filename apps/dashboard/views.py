from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Type

from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import View, ListView
from django.db.models import QuerySet, Model
from django.http import Http404
from django.forms import ModelForm

from apps.content.models import Category, Post, Tag, Page
from apps.content.utils.status import StatusAction
from apps.content.utils.contents import ContentQuery

from .forms import CategoryForm, PostForm, TagForm, PageForm
from .permissions import (
    SuperuserPermissionMixin,
    AuthorOrEditorMixin
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

    def get(self, request):
        return render(request, 'dashboard.html')


class AllContentView(AuthorOrEditorMixin, ListView, ABC):
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
        post_status = self.request.GET.get('post_status', 'all')
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        self.content_query = ContentQuery(self.model_class, self.request.user)

        queryset = self.content_query.get_posts_queryset(post_status)
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

    def render_to_response(self, context, **response_kwargs):
        content_context = self.content_context()
        if not content_context:
            raise Exception('Please provide required navigation urls')

        # Merge content counts and other data to the context
        context = {
            **context,
            **self.content_query.posts_count_by_status(),
            **asdict(self.content_context()),
            'title': self.title
        }
        return super().render_to_response(context, **response_kwargs)


class AllPostsView(AllContentView):
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


class AllPagesView(AllContentView):
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


class AbstractAddView(AuthorOrEditorMixin, View, ABC):
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

    def get(self, request):
        return render(request, self.template_name, {
            'update_mode': False,
            'title': self.title
        })

    def post(self, request):
        if not self.form:
            raise Exception('Please provide form class to validate input')

        form = self.form(data=request.POST)
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


class AbstractEditContentView(View, ABC):
    """
    This view handles the post which is already saved in the database.
    Set 'update_mode': True, so that template knows we are editing the post.
    """

    model_class: type[Model] = None
    edit_content_select_url: str = None
    # This path should accept the primary key argument
    edit_content_reverse_url_name: str = None

    def get(self, request, **kwargs):
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        pk = kwargs.get('pk')
        instance = get_object_or_404(self.model_class, pk=pk, is_trash=False)
        form = PostForm(instance=instance)

        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': True
        })

    def post(self, request, **kwargs):
        if not self.model_class:
            raise Exception('Please provide compatible model class')

        pk = kwargs.get('pk')
        action_type = request.GET.get('action', None)
        instance = get_object_or_404(self.model_class, pk=pk)

        # At first, check if there is any actions to perform like trash/restore/delete
        if action_type:
            action = StatusAction(instance)
            performed = action.perform(action_type)

            if performed:
                return redirect(self.edit_content_select_url)

        # Continue editing post
        # Don't allow to edit trash post
        if instance.is_trash:
            raise Http404()

        form = PostForm(instance=instance, data=request.POST)

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


class CategoriesView(View):
    def get(self, request):
        form = CategoryForm()

        return render(request, 'categories.html', {
            'form': form,
            'categories': Category.objects.all()
        })

    def post(self, request):
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('categories'))

        print(form.errors)
        return render(request, 'categories.html')


class TagsView(View):
    def get(self, request):
        form = TagForm()

        return render(request, 'tags.html', {
            'form': form,
            'tags': Tag.objects.all()
        })

    def post(self, request):
        form = TagForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('tags'))

        print(form.errors)
        return render(request, 'tags.html')


class MediaView(View):
    def get(self, request):
        return render(request, 'media.html')
