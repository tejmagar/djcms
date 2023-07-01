from rest_framework import serializers

from apps.media.models import Upload


class FileUploadSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField())


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ('file', 'id')
