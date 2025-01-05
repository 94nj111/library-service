from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
)
from borrowings_service.services import validate_user_payments


@extend_schema_view(
    list=extend_schema(
        summary="List Borrowings",
        description="Get a list of borrowings",
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active status",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID",
                required=False,
                type=int,
            ),
        ],
    ),
    create=extend_schema(
        summary="Create Borrowing", description="Create a new borrowing"
    ),
    retrieve=extend_schema(
        summary="Get Borrowing", description="Get details of a borrowing"
    ),
    update=extend_schema(summary="Update Borrowing", description="Update a borrowing"),
    partial_update=extend_schema(
        summary="Partial Update Borrowing", description="Partially update a borrowing"
    ),
    destroy=extend_schema(summary="Delete Borrowing", description="Delete a borrowing"),
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
        validate_user_payments(self.request)
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Return Borrowed Book",
        description="Mark a borrowed book as returned and update inventory.",
        responses={200: BorrowingSerializer},
    )
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
            raise PermissionDenied("You don't have permission to return this book.")

        if borrowing.expected_return_date < timezone.now().date():
            return redirect(reverse("payments:payments-create-session", kwargs={"pk": borrowing.id}))

        with transaction.atomic():
            book = borrowing.book
            book.inventory += 1
            book.save()

            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

        return Response(self.get_serializer(borrowing).data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 5, key_prefix="borrowing_view"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
