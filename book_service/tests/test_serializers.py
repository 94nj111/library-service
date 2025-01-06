from decimal import Decimal

from django.test import TestCase

from book_service.models import Book
from book_service.serializers import BookSerializer


class BookSerializerTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": Decimal("9.99"),
        }
        self.book = Book.objects.create(**self.book_data)
        self.serializer = BookSerializer(instance=self.book)

    def test_book_serializer(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_fee"},
        )
        self.assertEqual(data["title"], self.book_data["title"])
        self.assertEqual(data["author"], self.book_data["author"])
        self.assertEqual(data["cover"], self.book_data["cover"])
        self.assertEqual(data["inventory"], self.book_data["inventory"])
        self.assertEqual(Decimal(data["daily_fee"]), self.book_data["daily_fee"])
