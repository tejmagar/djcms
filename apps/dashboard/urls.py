from django.urls import path

from .views import (
    DashboardView,
    AddPostView,
    AllPostsView,
    EditPostView,
    CategoriesView,
    EditGroupView,
    TagsView,
    EditTagView,
    AbstractAllPagesView,
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

    # Categories and tags
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/edit/<int:pk>/', EditGroupView.as_view(), name='edit_category'),

    # Tags
    path('tags/', TagsView.as_view(), name='tags'),
    path('tags/edit/<int:pk>/', EditTagView.as_view(), name='edit_tag'),

    # Pages
    path('page/edit/', AbstractAllPagesView.as_view(), name='edit_page_select'),
    path('page/new/', AddPageView.as_view(), name='new_page'),
    path('page/edit/<int:pk>/', EditPageView.as_view(), name='edit_page'),

    path('media/', MediaView.as_view(), name='media')
]
