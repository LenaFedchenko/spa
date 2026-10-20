from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Attachment
from .tasks import process_attachment


@receiver(post_save, sender=Attachment)
def attachment_created(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(
            lambda: process_attachment.delay(instance.id)
        )
