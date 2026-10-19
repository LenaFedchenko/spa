from django.db import models
from comments.models import Comment


class Attachment(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(upload_to="attachments/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name