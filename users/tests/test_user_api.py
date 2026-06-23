from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = reverse("register")
TOKEN_URL = reverse("token-obtain")
ME_URL = reverse("me")


def create_user(**params):
    return User.objects.create_user(**params)


class RegisterTests(APITestCase):
    def test_register_success(self):
        payload = {
            "email": "test@test.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", res.data)

    def test_register_duplicate_email(self):
        create_user(email="test@test.com", password="testpass123")
        payload = {"email": "test@test.com", "password": "testpass123"}
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        payload = {"email": "test@test.com", "password": "123"}
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TokenTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="test@test.com", password="testpass123")

    def test_obtain_token_success(self):
        payload = {"email": "test@test.com", "password": "testpass123"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_obtain_token_wrong_password(self):
        payload = {"email": "test@test.com", "password": "wrongpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class MeTests(APITestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_me(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)

    def test_update_me(self):
        payload = {"first_name": "Jane"}
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")

    def test_me_unauthorized(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
