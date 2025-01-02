from rest_framework import viewsets

from core.book_service.models import Book
from core.book_service.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
