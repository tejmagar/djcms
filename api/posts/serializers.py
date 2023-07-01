from rest_framework import serializers

from apps.content.models import Post


class PostIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ('content',)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
