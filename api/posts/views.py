from rest_framework.generics import ListAPIView, GenericAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.content.models import Post
from .serializers import PostIndexSerializer, PostSerializer


class PostPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListView(ListAPIView):
    serializer_class = PostIndexSerializer
    queryset = Post.objects.filter(is_draft=False).order_by('-pk')
    pagination_class = PostPagination


class PostVIew(GenericAPIView):
    serializer_class = PostSerializer

    def get(self, request, **kwargs):
        slug = kwargs.get('slug')
        post = get_object_or_404(Post, slug=slug)
        serializer = self.serializer_class(instance=post)
        return Response(serializer.data)
