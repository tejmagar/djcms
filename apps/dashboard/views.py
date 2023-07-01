from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View
from apps.content.models import Post, Category, Tag

from django.shortcuts import reverse

from apps.content.models import Post
from .forms import PostForm, CategoryForm, TagForm


# Create your views here.

class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')


class AllPostsView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'all-posts.html', {
            'posts': posts
        })


class AddPostView(View):
    def get(self, request):
        return render(request, 'edit-post.html', {
            'update_mode': False
        })

    def post(self, request):
        form = PostForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('dashboard'))

        print(form.errors)
        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': False
        })


class EditPostView(View):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        page = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=page)

        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': True
        })

    def post(self, request, **kwargs):
        print(request.POST)
        pk = kwargs.get('pk')
        page = get_object_or_404(Post, pk=pk)
        form = PostForm(instance=page, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('edit_post', kwargs={'pk': pk}))

        return render(request, 'edit-post.html', {
            'form': form,
            'update_mode': True
        })


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
