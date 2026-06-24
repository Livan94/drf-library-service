from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()

BOOKS_URL = reverse("books-list")


def book_detail_url(book_id):
    return reverse("books-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": Book.CoverType.HARD,
        "inventory": 5,
        "daily_fee": "1.50",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class AnonymousPermissionsTests(APITestCase):
    def test_can_list_books(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_retrieve_book(self):
        book = sample_book()
        res = self.client.get(book_detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_create_book(self):
        payload = {
            "title": "New",
            "author": "Author",
            "cover": Book.CoverType.SOFT,
            "inventory": 1,
            "daily_fee": "1.00",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_delete_book(self):
        book = sample_book()
        res = self.client.delete(book_detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPermissionsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_can_list_books(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_create_book(self):
        payload = {
            "title": "New",
            "author": "Author",
            "cover": Book.CoverType.SOFT,
            "inventory": 1,
            "daily_fee": "1.00",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_book(self):
        book = sample_book()
        res = self.client.patch(book_detail_url(book.id), {"inventory": 99})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_book(self):
        book = sample_book()
        res = self.client.delete(book_detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPermissionsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)

    def test_can_create_book(self):
        payload = {
            "title": "Admin Book",
            "author": "Author",
            "cover": Book.CoverType.HARD,
            "inventory": 10,
            "daily_fee": "3.00",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_can_update_book(self):
        book = sample_book()
        res = self.client.patch(book_detail_url(book.id), {"inventory": 20})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_delete_book(self):
        book = sample_book()
        res = self.client.delete(book_detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
