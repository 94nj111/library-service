from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from book_service.models import Book
from borrowings_service.models import Borrowing

User = get_user_model()


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=5,
            daily_fee=1.50,
        )

    @patch("django.db.models.signals.ModelSignal.send")
    def test_borrowing_creation(self, mock_signal):
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )

        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertTrue(borrowing.is_active)

    @patch("django.db.models.signals.ModelSignal.send")
    def test_borrowing_constraints(self, mock_signal):
        with self.assertRaises(Exception):
            Borrowing.objects.create(
                borrow_date=timezone.now().date(),
                expected_return_date=timezone.now().date() - timezone.timedelta(days=1),
                book=self.book,
                user=self.user,
            )
