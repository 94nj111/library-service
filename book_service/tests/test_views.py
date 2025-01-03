from django.test import TestCase
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
        self.url = reverse("book_service:book-list")

    def test_get_book_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book(self):
        new_book_data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": "14.99",
        }
        response = self.client.post(self.url, new_book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        created_book = Book.objects.filter(title="New Book").first()
        self.assertIsNotNone(created_book, "Created book was not found.")
        self.assertEqual(created_book.title, "New Book")
        self.assertEqual(created_book.author, "New Author")

    def test_get_book_detail(self):
        url = reverse("book_service:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_update_book(self):
        url = reverse("book_service:book-detail", kwargs={"pk": self.book.pk})
        updated_data = {
            "title": "Updated Book",
            "author": self.book.author,
            "cover": self.book.cover,
            "inventory": self.book.inventory,
            "daily_fee": str(self.book.daily_fee),
        }
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book(self):
        url = reverse("book_service:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
