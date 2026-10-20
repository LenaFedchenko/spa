from celery import shared_task
from PIL import Image

from .models import Attachment


@shared_task
def process_attachment(attachment_id):
    attachment = Attachment.objects.get(
        id=attachment_id
    )

    if not attachment.file.name.lower().endswith(
        (".jpg", ".jpeg", ".png", ".gif")
    ):
        return "Not an image"

    with Image.open(attachment.file.path) as image:
        image.thumbnail((320, 240))
        image_format = image.format

        image.save(
            attachment.file.path,
            format=image_format
        )

    return f"Attachment {attachment_id} processed"
