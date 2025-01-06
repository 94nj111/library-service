from stripe.checkout import Session

from celery import shared_task
from django.utils import timezone
from .models import Payment
import stripe
from core.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


@shared_task
def check_expired_sessions():
    pending_payments = Payment.objects.filter(status="PENDING")

    for payment in pending_payments:
        try:
            session: Session = stripe.checkout.Session.retrieve(payment.session_id) # noqa
            if timezone.now() > payment.created_at + timezone.timedelta(hours=24):
                payment.status = "EXPIRED"
                payment.save()
        except stripe.error.StripeError:
            payment.status = "EXPIRED"
            payment.save()

    return f"Checked {pending_payments.count()} pending payments"
