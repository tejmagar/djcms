from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.media.models import Upload

from .serializers import FileSerializer, FileUploadSerializer


class UploadView(GenericAPIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileUploadSerializer
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            files = serializer.validated_data['files']
            last_upload = None

            for file in files:
                model = Upload.objects.create(file=file)
                model.uploaded_by = request.user
                # Auto generate content type
                model.clean()
                model.save()
                last_upload = model

            #
            if last_upload:
                return Response({
                    'location': last_upload.file.url
                })

        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class FilesListView(APIView):
    serializer_class = FileSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        filter_by = request.GET.get('filter_by')
        uploads = Upload.objects.get_queryset()

        if filter_by == 'image':
            uploads = uploads.filter(content_type__startswith='image')

        serializer = self.serializer_class(instance=uploads.order_by('-pk'), many=True)
        return Response(serializer.data)


class FileDelete(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pk = request.GET.get('id')
        upload = get_object_or_404(Upload, pk=pk)
        serializer = FileSerializer(instance=upload)
        return Response(serializer)

    def post(self, request):
        pk = request.GET.get('id')
        upload = get_object_or_404(Upload, pk=pk)
        upload.delete()
        return Response({})
