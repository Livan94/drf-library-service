import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()

BORROWINGS_URL = reverse("borrowings-list")


def borrowing_detail_url(borrowing_id):
    return reverse("borrowings-detail", args=[borrowing_id])


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


def sample_borrowing(user, **params):
    book = params.pop("book", sample_book())
    defaults = {
        "expected_return_date": datetime.date.today()
        + datetime.timedelta(days=7),
        "book": book,
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingTests(APITestCase):
    def test_list_requires_auth(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_borrowings(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_borrowing(self):
        borrowing = sample_borrowing(user=self.user)
        url = borrowing_detail_url(borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], borrowing.id)

    def test_book_detail_nested_in_borrowing(self):
        book = sample_book(title="Kobzar")
        borrowing = sample_borrowing(user=self.user, book=book)
        url = borrowing_detail_url(borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["book"]["title"], "Kobzar")

    def test_list_returns_only_own_borrowings(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
        )
        sample_borrowing(user=self.user)
        sample_borrowing(user=other_user)
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)


class BorrowingCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_borrowing_success(self):
        book = sample_book(inventory=3)
        payload = {
            "book": book.id,
            "expected_return_date": (
                datetime.date.today() + datetime.timedelta(days=7)
            ),
        }

        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, book)

        book.refresh_from_db()
        self.assertEqual(book.inventory, 2)

    def test_create_borrowing_with_zero_inventory(self):
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "expected_return_date": (
                datetime.date.today() + datetime.timedelta(days=7)
            ),
        }

        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_with_today_expected_return_date(self):
        book = sample_book(inventory=3)
        payload = {
            "book": book.id,
            "expected_return_date": datetime.date.today(),
        }

        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_unauthorized(self):
        self.client.force_authenticate(user=None)
        book = sample_book(inventory=3)
        payload = {
            "book": book.id,
            "expected_return_date": (
                datetime.date.today() + datetime.timedelta(days=7)
            ),
        }

        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
