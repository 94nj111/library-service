from rest_framework import serializers

from core.book_service.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book