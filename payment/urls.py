from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet, StripePaymentViewSet

router = DefaultRouter()
router.register("payments", PaymentViewSet)
router.register("payment", StripePaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "payment"
