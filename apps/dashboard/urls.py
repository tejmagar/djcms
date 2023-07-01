from django.urls import path

from .views import DashboardView, AllPostsView, AddPostView, EditPostView, CategoriesView, TagsView, MediaView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Posts
    path('post/edit/', AllPostsView.as_view(), name='edit_post_select'),
    path('post/new/', AddPostView.as_view(), name='new_post'),
    path('post/edit/<int:pk>/', EditPostView.as_view(), name='edit_post'),

    path('categories/', CategoriesView.as_view(), name='categories'),
    path('tags/', TagsView.as_view(), name='tags'),

    path('media/', MediaView.as_view(), name='media')
]
