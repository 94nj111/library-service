from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings_service.models import Borrowing
from payment.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book_details = serializers.SerializerMethodField()
    payments = PaymentSerializer(many=True)
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
            "payments",
        ]

    def get_book_details(self, obj):
        return {
            "title": obj.book.title,
            "author": obj.book.author,
            "inventory": obj.book.inventory,
        }

    # def get_payments(self, obj):
    #     from payment.serializers import PaymentSerializer
    #     return PaymentSerializer(obj.payments).data

class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["expected_return_date", "book"]

    def validate(self, data):
        book = data["book"]
        if book.inventory <= 0:
            raise ValidationError("Book inventory is not sufficient.")
        return data
