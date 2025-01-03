from rest_framework import serializers

from borrowings_service.serializers import BorrowingSerializer
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]
