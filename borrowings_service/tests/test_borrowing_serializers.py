from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from book_service.models import Book
from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingCreateSerializer,
    BorrowingSerializer,
)

User = get_user_model()


class BorrowingSerializerTests(TestCase):
    @patch("django.db.models.signals.ModelSignal.send")
    def setUp(self, mock_signal):
        self.user = User.objects.create_user(
            email="test3@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Book Serializer",
            author="Author",
            cover="SOFT",
            inventory=5,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )

    def test_borrowing_serializer(self):
        serializer = BorrowingSerializer(self.borrowing)
        data = serializer.data

        self.assertEqual(data["book_details"]["title"], "Book Serializer")
        self.assertEqual(data["user"], self.user.id)

    def test_borrowing_create_serializer(self):
        serializer = BorrowingCreateSerializer(
            data={
                "expected_return_date": timezone.now().date()
                + timezone.timedelta(days=7),
                "book": self.book.id,
            }
        )

        self.assertTrue(serializer.is_valid())

        self.book.inventory = 0
        self.book.save()
        serializer = BorrowingCreateSerializer(
            data={
                "expected_return_date": timezone.now().date()
                + timezone.timedelta(days=7),
                "book": self.book.id,
            }
        )

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
