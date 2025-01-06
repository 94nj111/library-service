from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from book_service.models import Book
from borrowings_service.models import Borrowing
from library_bot.bot import send_notification_on_borrowing_overdue, send_welcome


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
    @patch("library_bot.bot.save_user")
    def test_sign_for_a_bot(self, mock_save_user, mock_send_message):
        mock_message = MagicMock()
        mock_message.chat.id = 1

        send_welcome(mock_message)

        mock_send_message.assert_called_with(
            mock_message.chat.id,
            text="Greetings, I'm a library bot and"
            " from now on I'll be sending you notifications about: \n"
            " - new borrowing created, \n - borrowings overdue \n - successful payments",
        )

        mock_save_user.assert_called_with(mock_message.chat.id)

    @patch("library_bot.bot.bot.send_message")
    @patch("library_bot.bot.get_users")
    def test_get_notification_on_borrowing_creation(
        self, mock_get_users, mock_send_message
    ):
        mock_get_users.return_value = [1]

        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )

    @patch("library_bot.bot.bot.send_message")
    @patch("library_bot.bot.get_users")
    def test_borrowing_overdue_check(self, mock_get_users, mock_send_message):
        mock_get_users.return_value = [1]
        send_notification_on_borrowing_overdue()

        mock_send_message.assert_called_with(1, "No borrowings overdue today!")

    @patch("borrowings_service.signals.send_notification_on_borrowing_created")
    @patch("library_bot.bot.bot.send_message")
    @patch("library_bot.bot.get_users")
    def test_borrowing_overdue_check(
        self, mock_get_users, mock_send_message, mock_notification
    ):
        mock_get_users.return_value = [1]

        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date() - timezone.timedelta(days=1),
            expected_return_date=timezone.now().date() - timezone.timedelta(days=1),
            book=self.book,
            user=self.user,
        )

        send_notification_on_borrowing_overdue()

        mock_send_message.assert_called_with(
            1,
            f"Such borrows was overdue:\n"
            f"Book: {borrowing.book.title}\n"
            f"User email: {borrowing.user.email}\n"
            f"Expected return date: {borrowing.expected_return_date}\n"
            f"---------------------------------------\n",
        )
