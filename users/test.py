from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "Alex123",
                "email": "alex@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="Alex123").exists())
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login(self):
        User.objects.create_user(
            username="Alex123",
            email="alex@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "Alex123",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_me_requires_auth(self):
        response = self.client.get("/api/auth/me/")

        self.assertIn(response.status_code, [401, 403])
