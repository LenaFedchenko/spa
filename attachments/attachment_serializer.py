from pathlib import Path
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers
from .models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "comment", "file", "created_at"]
        read_only_fields = ["id", "created_at", "comment"]

    def validate_file(self, value):
        extension = Path(value.name).suffix.lower()

        allowed_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".txt"
        }

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Unsupported file format"
            )

        if extension == ".txt":
            if value.size > 100 * 1024:
                raise serializers.ValidationError(
                    "TXT file must be smaller than 100 KB"
                )

            try:
                value.seek(0)
                value.read().decode("utf-8")
            except UnicodeDecodeError:
                raise serializers.ValidationError(
                    "TXT file must use UTF-8 encoding"
                )
            finally:
                value.seek(0)

            return value

        try:
            value.seek(0)
            image = Image.open(value)
            image.verify()

            value.seek(0)
            image = Image.open(value)

            expected_formats = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".gif": "GIF",
            }

            if image.format != expected_formats[extension]:
                raise serializers.ValidationError(
                    "File content does not match its extension"
                )

            if getattr(image, "is_animated", False):
                raise serializers.ValidationError(
                    "Animated images are not supported"
                )

            image.thumbnail((320, 240))

            output = BytesIO()
            image_format = image.format

            image.save(output, format=image_format)
            output.seek(0)

            return InMemoryUploadedFile(
                output,
                "file",
                value.name,
                Image.MIME.get(image_format),
                output.getbuffer().nbytes,
                None,
            )

        except (UnidentifiedImageError, OSError, ValueError):
            raise serializers.ValidationError(
                "Invalid image file"
            )
