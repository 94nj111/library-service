from django.conf import settings
from django.db import models
from django.utils import timezone

from book_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @property
    def is_active(self):
        return self.actual_return_date is None

    def __str__(self):
        return f"Borrowing(User: {self.user}, book: {self.book.title}, borrow_date: {self.borrow_date})"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gte=models.F("borrow_date")),
                name="expected_return_after_borrow",
            )
        ]
