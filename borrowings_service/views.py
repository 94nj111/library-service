from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "actual_return_date"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        if user_id:
            if not user.is_staff:
                raise PermissionDenied(
                    "You do not have permission to perform this action."
                )
            return queryset.filter(user_id=user_id)

        if not user.is_staff:
            return queryset.filter(user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk=None):
        borrowing = get_object_or_404(Borrowing, pk=pk)

        if not borrowing.is_active:
            raise ValidationError("This book has already been returned.")

        if not request.user.is_staff and borrowing.user != request.user:
            raise PermissionDenied(
                "You don't have permission to return this book."
            )

        with transaction.atomic():
            book = borrowing.book
            book.inventory += 1
            book.save()

            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

        return Response(
            self.get_serializer(borrowing).data,
            status=status.HTTP_200_OK
        )

    @method_decorator(cache_page(60 * 5, key_prefix="borrowing_view"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
