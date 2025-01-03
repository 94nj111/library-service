from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book_details = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
            "book_details",
        ]

    def get_book_details(self, obj):
        return {
            "title": obj.book.title,
            "author": obj.book.author,
            "inventory": obj.book.inventory,
        }


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["expected_return_date", "book"]

    def validate(self, data):
        book = data["book"]
        if book.inventory <= 0:
            raise ValidationError("Book inventory is not sufficient.")
        return data
