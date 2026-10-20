from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from attachments.attachment_serializer import AttachmentSerializer
from comments.models import Comment



@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_attachment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    serializer = AttachmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attachment = serializer.save(comment=comment)

    return Response(serializer.data, status=201)
