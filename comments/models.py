from django.db import models
from django.conf import settings


class Comment(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    home_page = models.URLField(blank=True)

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    def __str__(self):
        return self.email
