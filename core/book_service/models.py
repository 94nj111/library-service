from django.db import models


COVER_CHOICES = (
    ("HARD", "Hard"),
    ("SOFT", "Soft"),
)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=5, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()       # Inventory – the number of this specific book available now in the library
    daily_free = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
