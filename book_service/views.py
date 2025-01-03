from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from book_service.models import Book
from book_service.permissions import IsAdminOrReadOnly
from book_service.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly, )

    @method_decorator(cache_page(60 * 5, key_prefix="book_view"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
