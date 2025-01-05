from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from book_service.models import Book
from borrowings_service.models import Borrowing
from payment.models import Payment


PAYMENT_URL = reverse("payments:payments-list")

class PaymentViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.user = get_user_model().objects.create_user("user1@test.com", "userpass")
        self.other_user = get_user_model().objects.create_user(
            "user2@test.com", "userpass"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="9.99",
        )
        self.other_book = Book.objects.create(
            title="Test Other Book",
            author="Test Other Author",
            cover="SOFT",
            inventory=20,
            daily_fee="19.99",
        )

        self.borrowing = Borrowing.objects.create(
            borrow_date="2024-01-01",
            expected_return_date="2024-01-02",
            book=self.book,
            user=self.user,
        )
        self.other_borrowing = Borrowing.objects.create(
            borrow_date="2024-01-01",
            expected_return_date="2024-01-02",
            book=self.other_book,
            user=self.other_user,
        )

        self.payment = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing,
            session_url="http://example.com",
            session_id="123",
            money_to_pay=10.00,
        )
        self.other_payment = Payment.objects.create(
            status="PAID",
            type="FINE",
            borrowing=self.other_borrowing,
            session_url="http://example.com",
            session_id="456",
            money_to_pay=15.00,
        )

    def test_admin_can_view_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_can_view_own_payments(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_view_others_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("payments:payments-detail", kwargs={"pk": self.other_payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        """
        Admin Auth: Check if this response and payment exist and not 404
        (example, if response not correct, it will be also 404 and it needs to be checked)        
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("payments:payments-detail", kwargs={"pk": self.other_payment.id})
        )
        reverse("book_service:book-detail", kwargs={"pk": self.book.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_access_payments(self):
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_stripe_session(self):
        self.client.force_authenticate(user=self.user)
        borrowing_id = self.borrowing.id
        response = self.client.post(
            reverse("payments:payments-create-session", kwargs={"pk": borrowing_id})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("session_url", response.data)
        self.assertIn("session_id", response.data)

    def test_create_stripe_session_for_non_existing_borrowing(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/payments/payments/999/create-session/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_payment(self):
        self.client.force_authenticate(user=self.user)
        borrowing_id = self.borrowing.id
        response = self.client.post(
            reverse("payments:payments-create-session", kwargs={"pk": borrowing_id})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session_id = response.data["session_id"]
        response = self.client.get(
            f"/api/payments/payments/success/?session_id={session_id}"
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        if response.status_code == status.HTTP_202_ACCEPTED:
            payment = Payment.objects.get(session_id=session_id)
            self.assertEqual(payment.status, "PENDING")
        if response.status_code == status.HTTP_200_OK:
            payment = Payment.objects.get(session_id=session_id)
            self.assertEqual(payment.status, "PAID")

    def test_successful_payment_without_session_id(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            "/api/payments/payments/success/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Session ID is required")

    def test_cancel_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            "/api/payments/payments/cancel/",
            {"session_id": self.payment.session_id},
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"],
            "The payment can be made later, "
            "but the session is available for only 24 hours.",
        )

    def test_cancel_payment_without_session_id(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            "/api/payments/payments/cancel/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Session ID is required", str(response.data))
