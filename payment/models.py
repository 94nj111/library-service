from django.db import models

from borrowings_service.models import Borrowing

STATUS_CHOICES = (
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
)

TYPE_CHOICES = (
    ("PAYMENT", "Payment"),
    ("FINE", "Fine"),
)


class Payment(models.Model):
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Payment {self.session_id} ({self.status})"
