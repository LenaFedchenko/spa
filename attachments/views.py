from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from attachments.attachment_serializer import AttachmentSerializer
from comments.models import Comment

# Create your views here.


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_attachment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    serializer = AttachmentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(comment=comment)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
