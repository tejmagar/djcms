import mimetypes

from django.db import models

from django.contrib.auth import get_user_model


# Create your models here.


class Upload(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(to=get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to='uploads/')
    content_type = models.CharField(max_length=60, null=True, blank=True)

    def clean(self):
        if not self.content_type:
            content_type, _ = mimetypes.guess_type(self.file.path)
            self.content_type = content_type

    def __str__(self):
        return self.file.name
