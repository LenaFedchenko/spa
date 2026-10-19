from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from comments.models import Comment
from comments.serializers import CommentSerializer, CreateCommentSerializer
from rest_framework.pagination import PageNumberPagination
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


@api_view(["GET"])
def get_comments(request):
    sort = request.query_params.get("sort", "created_at")
    order = request.query_params.get("order", "desc")
    allowed_fields = ["user_name", "email", "created_at"]

    if sort not in allowed_fields:
        return Response({"error": "Invalid sort field"}, status=400)

    if order not in ["asc", "desc"]:
        return Response({"error": "Invalid order"}, status=400)

    if order == "desc":
        sort = "-" + sort

    comments = Comment.objects.filter(parent__isnull=True).order_by(sort, "-id")
    pagination = PageNumberPagination()
    pagination.page_size = 25
    page = pagination.paginate_queryset(comments, request)

    serializer = CommentSerializer(page, many=True)

    return pagination.get_paginated_response(serializer.data)



@api_view(["GET"])
def get_comment(request, id):
    comment_by_id = get_object_or_404(Comment, id=id)
    serializer = CommentSerializer(comment_by_id)
    return Response(serializer.data)

@api_view(["POST"])
def create_comment(request):
    serializer = CreateCommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(parent=None)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



@api_view(["GET", "POST"])
def manage_replies(request, id):
    parent = get_object_or_404(Comment, id=id)

    if request.method == "GET":
        replies = Comment.objects.filter(parent=parent)
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

    serializer = CreateCommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(parent=parent)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)





@api_view(["GET"])
def get_captcha(request):
    key = CaptchaStore.generate_key()

    return Response({
        "captcha_hashkey": key,
        "image_url": request.build_absolute_uri(
            captcha_image_url(key)
        )
    })

