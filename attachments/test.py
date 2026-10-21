from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from attachments.attachment_serializer import AttachmentSerializer



class AttachmentTests(TestCase):
    def test_large_txt_file(self):
        file = SimpleUploadedFile(
            "large.txt",
            b"A" * (101 * 1024),
            content_type="text/plain",
        )

        serializer = AttachmentSerializer()

        with self.assertRaises(Exception):
            serializer.validate_file(file)
