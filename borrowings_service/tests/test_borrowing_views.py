from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from borrowings_service.models import Borrowing
from book_service.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class BorrowingViewsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="admin123"
        )
        self.book = Book.objects.create(
            title="View Book",
            author="Author",
            cover="HARD",
            inventory=5,
            daily_fee=1.00,
        )

    def test_list_borrowings(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/borrowings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_borrowing(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "expected_return_date": timezone.now().date() + timezone.timedelta(days=7),
            "book": self.book.id,
        }
        response = self.client.post("/api/borrowings/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/borrowings/?user_id={self.user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_denied_for_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/borrowings/?user_id=1")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_is_active(self):
        self.client.force_authenticate(user=self.user)
        Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        response = self.client.get("/api/borrowings/?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_is_not_active(self):
        self.client.force_authenticate(user=self.user)
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            actual_return_date=timezone.now().date(),
            book=self.book,
            user=self.user,
        )
        response = self.client.get("/api/borrowings/?is_active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_return_borrowing_success(self):
        self.client.force_authenticate(user=self.user)
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        initial_inventory = self.book.inventory
        response = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory + 1)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_return_borrowing_already_returned(self):
        self.client.force_authenticate(user=self.user)
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            actual_return_date=timezone.now().date(),
            book=self.book,
            user=self.user,
        )
        response = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing_unauthorized_user(self):
        self.client.force_authenticate(user=self.user)
        other_user = User.objects.create_user(
            email="other@example.com", password="password123"
        )
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=other_user,
        )
        response = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_return_borrowing_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        initial_inventory = self.book.inventory
        response = self.client.post(f"/api/borrowings/{borrowing.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory + 1)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
