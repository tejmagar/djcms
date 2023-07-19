from django.urls import path

from .views import (
    DashboardView,
    AddPostView,
    AllPostsView,
    EditPostView,
    CategoriesView,
    TagsView,
    AllPagesView,
    AddPageView,
    EditPageView,
    MediaView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Posts
    path('post/edit/', AllPostsView.as_view(), name='edit_post_select'),
    path('post/new/', AddPostView.as_view(), name='new_post'),
    path('post/edit/<int:pk>/', EditPostView.as_view(), name='edit_post'),

    path('categories/', CategoriesView.as_view(), name='categories'),
    path('tags/', TagsView.as_view(), name='tags'),

    # Pages
    path('page/edit/', AllPagesView.as_view(), name='edit_page_select'),
    path('page/new/', AddPageView.as_view(), name='new_page'),
    path('page/edit/<int:pk>/', EditPageView.as_view(), name='edit_page'),

    path('media/', MediaView.as_view(), name='media')
]
