from decimal import Decimal

from django.test import TestCase

from book_service.models import Book


class BookModelTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": Decimal("9.99"),
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
        self.assertEqual(self.book.daily_fee, self.book_data["daily_fee"])
