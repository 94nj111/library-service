from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from book_service.models import Book
from borrowings_service.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentSerializerTests(APITestCase):
    def setUp(self):
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
            user=self.user
        )
        self.payment_data = {
            "status": "PENDING",
            "type": "PAYMENT",
            "borrowing": self.borrowing,
            "session_url": "https://example.com/session",
            "session_id": "123-session-id",
            "money_to_pay": "50.00"
        }

    def test_payment_serializer_valid_data(self):
        data = {
            "status": self.payment_data["status"],
            "type": self.payment_data["type"],
            "borrowing": {
                "borrow_date": "2024-01-01",
                "expected_return_date": "2024-01-02",
                "book": self.book.id,
                "user": self.user.id
            },
            "session_url": self.payment_data["session_url"],
            "session_id": self.payment_data["session_id"],
            "money_to_pay": self.payment_data["money_to_pay"]
        }

        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_payment_serializer_invalid_status(self):
        invalid_data = self.payment_data.copy()
        invalid_data["status"] = "INVALID_STATUS"

        serializer = PaymentSerializer(data=invalid_data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_payment_serializer_invalid_type(self):
        invalid_data = self.payment_data.copy()
        invalid_data["type"] = "INVALID_TYPE"

        serializer = PaymentSerializer(data=invalid_data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_payment_serializer_money_to_pay_negative(self):
        invalid_data = self.payment_data.copy()
        invalid_data["money_to_pay"] = "-10.00"

        serializer = PaymentSerializer(data=invalid_data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_payment_serializer_output_format(self):
        payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://example.com/session",
            session_id="123-session-id",
            money_to_pay="50.00"
        )

        serializer = PaymentSerializer(payment)
        data = serializer.data

        self.assertEqual(data["status"], "PENDING")
        self.assertEqual(data["type"], "PAYMENT")
        self.assertEqual(data["session_url"], "https://example.com/session")
        self.assertEqual(data["session_id"], "123-session-id")
        self.assertEqual(data["money_to_pay"], "50.00")
