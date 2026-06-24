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


def create_user(**params):
    return User.objects.create_user(**params)


class PublicBooksApiTests(APITestCase):
    def test_list_books_unauthenticated(self):
        sample_book()
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_book_unauthenticated(self):
        book = sample_book()
        url = book_detail_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_unauthenticated(self):
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": Book.CoverType.SOFT,
            "inventory": 3,
            "daily_fee": "2.00",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="user@test.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

    def test_list_books_authenticated(self):
        sample_book()
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_book_authenticated(self):
        book = sample_book()
        url = book_detail_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], book.title)


class AdminBooksApiTests(APITestCase):
    def setUp(self):
        self.admin = create_user(
            email="admin@test.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_book_admin(self):
        payload = {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": Book.CoverType.HARD,
            "inventory": 10,
            "daily_fee": "3.00",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        self.assertEqual(book.title, payload["title"])

    def test_update_book_admin(self):
        book = sample_book()
        payload = {"inventory": 20}
        url = book_detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.inventory, 20)

    def test_delete_book_admin(self):
        book = sample_book()
        url = book_detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
