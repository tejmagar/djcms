from django.urls import path

from .views import (
    DashboardView,
    AddPostView,
    AllPostsView,
    EditPostView,
    CategoriesView,
    EditCategoryView,
    TagsView,
    EditTagView,
    AllPagesView,
    AddPageView,
    EditPageView,
    MediaView,
    AllUsers,
    AddUser,
    EditUserView,
    UserProfileView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Posts
    path('post/edit/', AllPostsView.as_view(), name='edit_post_select'),
    path('post/new/', AddPostView.as_view(), name='new_post'),
    path('post/edit/<int:pk>/', EditPostView.as_view(), name='edit_post'),

    # Categories and tags
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('categories/edit/<int:pk>/', EditCategoryView.as_view(), name='edit_category'),

    # Tags
    path('tags/', TagsView.as_view(), name='tags'),
    path('tags/edit/<int:pk>/', EditTagView.as_view(), name='edit_tag'),

    # Pages
    path('page/edit/', AllPagesView.as_view(), name='edit_page_select'),
    path('page/new/', AddPageView.as_view(), name='new_page'),
    path('page/edit/<int:pk>/', EditPageView.as_view(), name='edit_page'),

    # Users
    path('users/', AllUsers.as_view(), name='all_users'),
    path('users/add/', AddUser.as_view(), name='add_user'),
    path('users/edit/<int:pk>/', EditUserView.as_view(), name='edit_user'),
    path('users/profile/', UserProfileView.as_view(), name='edit_profile'),

    path('media/', MediaView.as_view(), name='media')
]
