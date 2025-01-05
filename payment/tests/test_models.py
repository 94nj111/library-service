from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from book_service.models import Book
from borrowings_service.models import Borrowing
from payment.models import Payment


class PaymentModelTest(TestCase):
    @patch("django.db.models.signals.ModelSignal.send")
    def setUp(self, mock_signal):
        self.user = get_user_model().objects.create_user("user1@test.com", "userpass")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="9.99",
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date="2024-01-01",
            expected_return_date="2024-01-02",
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://example.com/payment",
            session_id="session_123456",
            money_to_pay=Decimal("100.00"),
        )

    def test_payment_creation(self):
        """Test if payment instance is created successfully."""
        self.assertEqual(self.payment.status, "PENDING")
        self.assertEqual(self.payment.type, "PAYMENT")
        self.assertEqual(self.payment.borrowing, self.borrowing)
        self.assertEqual(self.payment.session_url, "https://example.com/payment")
        self.assertEqual(self.payment.session_id, "session_123456")
        self.assertEqual(self.payment.money_to_pay, Decimal("100.00"))

    def test_payment_str_method(self):
        """Test the __str__ method of the Payment model."""
        self.assertEqual(str(self.payment), "Payment session_123456 (PENDING)")

    def test_payment_status_choices(self):
        """Test the status field choices."""
        choices = dict(Payment._meta.get_field("status").choices)
        self.assertIn("PENDING", choices)
        self.assertIn("PAID", choices)

    def test_payment_type_choices(self):
        """Test the type field choices."""
        choices = dict(Payment._meta.get_field("type").choices)
        self.assertIn("PAYMENT", choices)
        self.assertIn("FINE", choices)

    def test_money_to_pay_decimal_field(self):
        """Test that money_to_pay supports decimals correctly."""
        self.payment.money_to_pay = Decimal("150.50")
        self.payment.save()
        self.assertEqual(self.payment.money_to_pay, Decimal("150.50"))

    def test_invalid_status(self):
        """Test if invalid status raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.payment.status = "INVALID"
            self.payment.full_clean()
