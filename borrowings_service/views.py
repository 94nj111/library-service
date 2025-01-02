from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

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
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)
        if not user.is_staff:
            return queryset.filter(user=user)
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return queryset.filter(user_id=user_id)
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
