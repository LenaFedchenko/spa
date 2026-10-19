
import re

from rest_framework import serializers
from captcha.serializers import CaptchaModelSerializer

from .models import Comment
from .validators import validate_comment_html


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "user_name",
            "email",
            "home_page",
            "text",
            "created_at",
            "parent",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "parent",
        ]

    def validate_user_name(self, value):
        if not re.fullmatch(r"[a-zA-Z0-9]+", value):
            raise serializers.ValidationError(
                "Only Latin letters and numbers are allowed"
            )

        return value

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Text cannot be empty"
            )

        return validate_comment_html(value)


class CreateCommentSerializer(CaptchaModelSerializer, CommentSerializer):
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + [
            "captcha_code",
            "captcha_hashkey",
        ]

    def create(self, validated_data):
        validated_data.pop("captcha_code", None)
        validated_data.pop("captcha_hashkey", None)

        return super().create(validated_data)
