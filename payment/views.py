from decimal import Decimal

import stripe
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets

import stripe

from rest_framework import status, mixins, viewsets

from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from core.settings import STRIPE_SECRET_KEY
from library_bot.bot import send_notification_on_success_payment
from payment.models import Borrowing, Payment
from payment.serializers import PaymentSerializer

stripe.api_key = STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2


@extend_schema(
    summary="Create Payment Session",
    description="Create a Stripe payment session for borrowing",
    request=None,
    responses={201: PaymentSerializer},
)
class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Admin see all payments, user - only his own"""

        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)

    @action(detail=True, methods=["post"], url_path="create-session")
    def create_session(self, request, pk=None):
        """
        Create a Stripe payment session for a specific borrowing.
        """
        borrowing = get_object_or_404(Borrowing, id=pk)

        try:
            with transaction.atomic():
                is_fine = False
                fine_amount = Decimal(0)
                actual_date = timezone.now().date()

                if borrowing.expected_return_date < actual_date:
                    overdue_days = (actual_date - borrowing.expected_return_date).days
                    if overdue_days > 0:
                        is_fine = True
                        fine_amount = Decimal(
                            overdue_days * borrowing.book.daily_fee * FINE_MULTIPLIER
                        )

                payment_type = "FINE" if is_fine else "PAYMENT"
                amount = (
                    fine_amount
                    if is_fine
                    else Decimal(
                        borrowing.book.daily_fee
                        * (borrowing.expected_return_date - borrowing.borrow_date).days
                    )
                )

                if borrowing.actual_return_date:
                    is_fine = borrowing.actual_return_date > borrowing.expected_return_date
                payment_type = "FINE" if is_fine else "PAYMENT"
                amount = Decimal(borrowing.book.daily_fee * (borrowing.expected_return_date - borrowing.borrow_date).days)
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": f"Borrowing: {borrowing.book.title}"
                                },
                                "unit_amount": int(amount * 100)
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="payment",
                    success_url=request.build_absolute_uri("/payments/success/")
                    + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=request.build_absolute_uri("/payments/cancel/"),
                )

                Payment.objects.create(
                    borrowing=borrowing,
                    session_id=session.id,
                    session_url=session.url,
                    type=payment_type,
                    money_to_pay=amount,
                    status="PENDING",
                )

                return Response(
                    {"session_url": session.url, "session_id": session.id},
                    status=status.HTTP_201_CREATED,
                )

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request):
        """
        Handle successful payment callback.
        """
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                payment = Payment.objects.get(session_id=session_id)
                payment.status = "PAID"
                payment.save()
                if payment.borrowing.expected_return_date < timezone.now().date():
                    payment.borrowing.actual_return_date = timezone.now().date()

                send_notification_on_success_payment(payment)

                return Response(
                    {"message": "Payment successful", "session_id": session_id},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Payment not completed yet"},
                status=status.HTTP_202_ACCEPTED,
            )

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment record not found for the provided session_id"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        """
        Handle payment cancellation callback.
        """
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "The payment can be made later,"
                " but the session is available for only 24 hours."
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["POST"])
    def renew_session(self, request, pk=None):
        payment = self.get_object()
        if payment.status != "EXPIRED":
            return Response(
                {"error": "Only expired payments can be renewed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Borrowing: {payment.borrowing.book_title}"
                            },
                            "unit_amount": int(payment.money_to_pay * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri("/payment/success/")
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri("/payment/cancel/"),
            )

            payment.session_id = new_session.id
            payment.session_url = new_session.url
            payment.status = "PENDING"
            payment.save()

            return Response(
                {"session_url": new_session.url, "session_id": new_session.id},
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
