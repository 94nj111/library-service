from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from book_service.models import Book
from borrowings_service.models import Borrowing
from library_bot.bot import send_notification_on_borrowing_overdue, CHAT_ID, get_id


class TestBot(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test",
            author="Test",
            cover="HARD",
            inventory=5,
            daily_fee=1.50,
        )

        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test"
        )

    @patch("library_bot.bot.bot.send_message")
    def test_get_id(self, mock_send_message):
        mock_message = MagicMock()
        mock_message.chat.id = 1542351

        get_id(mock_message)

        mock_send_message.assert_called_with(1542351, 1542351)

    @patch("library_bot.bot.bot.send_message")
    def test_get_notification_on_borrowing_creation(self, mock_get_users):
        mock_get_users.return_value = [1]

        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )

    @patch("library_bot.bot.bot.send_message")
    def test_borrowing_overdue_check(self, mock_send_message):
        send_notification_on_borrowing_overdue()

        mock_send_message.assert_called_with(CHAT_ID, "No borrowings overdue today!")

    @patch("borrowings_service.signals.send_notification_on_borrowing_created")
    @patch("library_bot.bot.bot.send_message")
    def test_borrowing_overdue_check(self, mock_send_message, mock_notification):
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date() - timezone.timedelta(days=1),
            expected_return_date=timezone.now().date() - timezone.timedelta(days=1),
            book=self.book,
            user=self.user,
        )

        send_notification_on_borrowing_overdue()

        mock_send_message.assert_called_with(
            CHAT_ID,
            f"Such borrows was overdue:\n"
            f"Book: {borrowing.book.title}\n"
            f"User email: {borrowing.user.email}\n"
            f"Expected return date: {borrowing.expected_return_date}\n"
            f"---------------------------------------\n",
        )
