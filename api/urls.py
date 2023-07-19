from django.urls import path

from .media.views import FileDelete, FilesListView, UploadView
from .posts.views import PostListView, PostVIew

urlpatterns = [
    path('v1/posts/', PostListView.as_view(), name='posts'),
    path('v1/post/<str:slug>/', PostVIew.as_view(), name='post'),

    path('v1/files/upload/', UploadView.as_view(), name='upload_file'),
    path('v1/files/', FilesListView.as_view(), name='uploaded_files'),
    path('v1/files/delete/', FileDelete.as_view(), name='delete_file'),
]
