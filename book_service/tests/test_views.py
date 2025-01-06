from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book_service.models import Book


class BookViewSetTest(APITestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "9.99",
        }
        self.book = Book.objects.create(**self.book_data)
        self.url = reverse("book_service:books-list")
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.user = get_user_model().objects.create_user("user@test.com", "userpass")

    def test_get_book_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_unauthenticated(self):
        data = self.book_data
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_admin(self):
        new_book_data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": "14.99",
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, new_book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        created_book = Book.objects.filter(title="New Book").first()
        self.assertIsNotNone(created_book, "Created book was not found.")
        self.assertEqual(created_book.title, "New Book")
        self.assertEqual(created_book.author, "New Author")

    def test_create_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = self.book_data
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_unauthenticated(self):
        data = self.book_data
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_book_detail(self):
        url = reverse("book_service:books-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_update_book_admin(self):
        url = reverse("book_service:books-detail", kwargs={"pk": self.book.pk})
        updated_data = {
            "title": "Updated Book",
            "author": self.book.author,
            "cover": self.book.cover,
            "inventory": self.book.inventory,
            "daily_fee": str(self.book.daily_fee),
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book_admin(self):
        url = reverse("book_service:books-detail", kwargs={"pk": self.book.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_delete_book_unauthenticated(self):
        url = reverse("book_service:books-detail", kwargs={"pk": self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_as_user(self):
        url = reverse("book_service:books-detail", kwargs={"pk": self.book.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
