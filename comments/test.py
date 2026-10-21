from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from captcha.models import CaptchaStore

from .models import Comment


class CommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def create_captcha(self):
        captcha = CaptchaStore.generate_key()
        answer = CaptchaStore.objects.get(hashkey=captcha).response
        return captcha, answer

    def comment_data(self):
        key, answer = self.create_captcha()

        return {
            "user_name": "Alex123",
            "email": "alex@example.com",
            "home_page": "",
            "text": "<strong>Hello</strong>",
            "captcha_hashkey": key,
            "captcha_code": answer,
        }

    def test_create_comment(self):
        response = self.client.post(
            "/comments/create/",
            self.comment_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

    def test_invalid_captcha(self):
        data = self.comment_data()
        data["captcha_code"] = "wrong"

        response = self.client.post(
            "/comments/create/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    def test_invalid_html(self):
        data = self.comment_data()
        data["text"] = "<strong>Hello"

        response = self.client.post(
            "/comments/create/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_script_is_not_saved(self):
        data = self.comment_data()
        data["text"] = "<script>alert(1)</script>"

        response = self.client.post(
            "/comments/create/",
            data,
            format="json",
        )

        if response.status_code == 201:
            comment = Comment.objects.first()
            self.assertNotIn("<script", comment.text.lower())
        else:
            self.assertEqual(response.status_code, 400)

    def test_create_reply(self):
        parent = Comment.objects.create(
            user_name="Alex",
            email="alex@example.com",
            text="Parent",
        )

        response = self.client.post(
            f"/comments/{parent.id}/replies/",
            self.comment_data(),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.get(parent=parent).user_name, "Alex123")

    def test_pagination(self):
        for number in range(30):
            Comment.objects.create(
                user_name=f"User{number}",
                email=f"user{number}@example.com",
                text="Test",
            )

        response = self.client.get("/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 30)
        self.assertEqual(len(response.data["results"]), 25)

    def test_sort_by_name(self):
        for name in ["Charlie", "Alice", "Bob"]:
            Comment.objects.create(
                user_name=name,
                email=f"{name.lower()}@example.com",
                text="Test",
            )

        response = self.client.get("/comments/?sort=user_name&order=asc")

        names = [
            comment["user_name"]
            for comment in response.data["results"]
        ]

        self.assertEqual(names, ["Alice", "Bob", "Charlie"])
