from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="borrowing.user.email")

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "user_email",
            "session_url",
            "session_id",
            "money_to_pay",
        ]
