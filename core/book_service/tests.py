from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.book_service.models import Book
from core.book_service.serializers import BookSerializer
from decimal import Decimal


class BookModelTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_free": Decimal("9.99")
        }
        self.book = Book.objects.create(**self.book_data)

    def test_book_creation(self):
        self.assertTrue(isinstance(self.book, Book))
        self.assertEqual(str(self.book), self.book.title)

    def test_book_fields(self):
        self.assertEqual(self.book.title, self.book_data["title"])
        self.assertEqual(self.book.author, self.book_data["author"])
        self.assertEqual(self.book.cover, self.book_data["cover"])
        self.assertEqual(self.book.inventory, self.book_data["inventory"])
        self.assertEqual(self.book.daily_free, self.book_data["daily_free"])

class BookSerializerTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_free": Decimal("9.99")
        }
        self.book = Book.objects.create(**self.book_data)
        self.serializer = BookSerializer(instance=self.book)

    def test_book_serializer(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_free"}
        )
        self.assertEqual(data["title"], self.book_data["title"])
        self.assertEqual(data["author"], self.book_data["author"])
        self.assertEqual(data["cover"], self.book_data["cover"])
        self.assertEqual(data["inventory"], self.book_data["inventory"])
        self.assertEqual(Decimal(data["daily_free"]), self.book_data["daily_free"])

class BookViewSetTest(APITestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_free": "9.99"
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
            "daily_free": "14.99"
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
            "daily_free": str(self.book.daily_free)
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
