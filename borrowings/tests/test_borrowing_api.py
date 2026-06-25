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
        "expected_return_date": datetime.date.today() + datetime.timedelta(days=7),
        "book": book,
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def borrowing_return_url(borrowing_id):
    return reverse("borrowings-return-borrowing", args=[borrowing_id])


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
        self.assertEqual(len(res.data["results"]), 2)

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
        self.assertGreaterEqual(len(res.data["results"]), 1)


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


class BorrowingFilteringTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="adminpass123",
            is_staff=True,
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
        )

    def test_regular_user_sees_only_own_borrowings(self):
        self.client.force_authenticate(user=self.user)
        own_borrowing = sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], own_borrowing.id)

    def test_regular_user_cannot_access_other_user_detail(self):
        self.client.force_authenticate(user=self.user)
        other_borrowing = sample_borrowing(user=self.other_user)

        res = self.client.get(borrowing_detail_url(other_borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_sees_all_borrowings(self):
        self.client.force_authenticate(user=self.admin)
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_admin_can_filter_by_user_id(self):
        self.client.force_authenticate(user=self.admin)
        user_borrowing = sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL, {"user_id": self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], user_borrowing.id)

    def test_regular_user_cannot_use_user_id_to_see_others(self):
        self.client.force_authenticate(user=self.user)
        own_borrowing = sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL, {"user_id": self.other_user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], own_borrowing.id)

    def test_filter_is_active_true(self):
        self.client.force_authenticate(user=self.admin)
        active_borrowing = sample_borrowing(
            user=self.user,
            actual_return_date=None,
        )
        sample_borrowing(
            user=self.user,
            actual_return_date=datetime.date.today(),
        )

        res = self.client.get(BORROWINGS_URL, {"is_active": "true"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], active_borrowing.id)

    def test_filter_is_active_false(self):
        self.client.force_authenticate(user=self.admin)
        sample_borrowing(
            user=self.user,
            actual_return_date=None,
        )
        returned_borrowing = sample_borrowing(
            user=self.user,
            actual_return_date=datetime.date.today(),
        )

        res = self.client.get(BORROWINGS_URL, {"is_active": "false"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], returned_borrowing.id)


class BorrowingReturnTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_return_borrowing_success(self):
        book = sample_book(inventory=0)
        borrowing = sample_borrowing(
            user=self.user,
            book=book,
            actual_return_date=None,
        )

        res = self.client.post(borrowing_return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

        book.refresh_from_db()
        self.assertEqual(book.inventory, 1)

    def test_return_borrowing_twice_not_allowed(self):
        borrowing = sample_borrowing(
            user=self.user,
            actual_return_date=datetime.date.today(),
        )

        res = self.client.post(borrowing_return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user_cannot_return_borrowing(self):
        borrowing = sample_borrowing(user=self.user)
        self.client.force_authenticate(user=None)

        res = self.client.post(borrowing_return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_return_other_user_borrowing(self):
        borrowing = sample_borrowing(user=self.other_user)

        res = self.client.post(borrowing_return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
