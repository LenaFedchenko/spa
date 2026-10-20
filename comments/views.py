from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from comments.models import Comment
from comments.serializers import CommentSerializer, CreateCommentSerializer
from rest_framework.pagination import PageNumberPagination
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.core.cache import cache



@api_view(["GET"])
def get_comments(request):
    sort = request.query_params.get("sort", "created_at")
    order = request.query_params.get("order", "desc")
    allowed_fields = ["user_name", "email", "created_at"]

    if sort not in allowed_fields:
        return Response({"error": "Invalid sort field"}, status=400)

    if order not in ["asc", "desc"]:
        return Response({"error": "Invalid order"}, status=400)

    page_number = request.query_params.get("page", "1")
    version = cache.get("comments_version", 1)
    cache_key = f"comments:{version}:{sort}:{order}:{page_number}"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response(cached_data)
    if order == "desc":
        sort = "-" + sort

    comments = Comment.objects.filter(
        parent__isnull=True
    ).order_by(sort, "-id")

    pagination = PageNumberPagination()
    pagination.page_size = 25
    page = pagination.paginate_queryset(comments, request)

    serializer = CommentSerializer(page, many=True)
    response = pagination.get_paginated_response(
        serializer.data
    )
    cache.set(cache_key, response.data, timeout=600)
    print("CACHE KEY:", cache_key)
    print("CACHE SAVED:", cache.get(cache_key) is not None)

    return response




@api_view(["GET"])
def get_comment(request, id):
    comment_by_id = get_object_or_404(Comment, id=id)
    serializer = CommentSerializer(comment_by_id)
    return Response(serializer.data)



def send_comment_event(comment):
    channel_layer = get_channel_layer()

    serializer = CommentSerializer(comment)

    async_to_sync(channel_layer.group_send)(
        "comments",
        {
            "type": "comment.created",
            "comment": serializer.data
        }
    )



@api_view(["POST"])
def create_comment(request):
    serializer = CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    comment = serializer.save(user=user, parent=None)
    transaction.on_commit(invalidate_comments_cache)
    transaction.on_commit(lambda: send_comment_event(comment))

    return Response(serializer.data, status=201)







@api_view(["GET", "POST"])
def manage_replies(request, id):
    parent = get_object_or_404(Comment, id=id)
    if request.method == "GET":
        replies = Comment.objects.filter(parent=parent)
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

    serializer = CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    comment = serializer.save(user=user, parent=parent)
    transaction.on_commit(invalidate_comments_cache)
    transaction.on_commit(lambda: send_comment_event(comment))

    return Response(serializer.data, status=201)







@api_view(["GET"])
def get_captcha(request):
    key = CaptchaStore.generate_key()

    return Response({
        "captcha_hashkey": key,
        "image_url": request.build_absolute_uri(
            captcha_image_url(key)
        )
    })

def invalidate_comments_cache():
    try:
        cache.incr("comments_version")
    except ValueError:
        cache.set("comments_version", 1, timeout=None)