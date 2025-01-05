# Generated by Django 5.1.4 on 2025-01-05 14:24

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("borrowings_service", "0002_alter_borrowing_book_alter_borrowing_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("PAID", "Paid"),
                            ("EXPIRED", "Expired"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("PAYMENT", "Payment"), ("FINE", "Fine")],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("session_url", models.URLField()),
                ("session_id", models.CharField(max_length=255)),
                (
                    "money_to_pay",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="borrowings_service.borrowing",
                    ),
                ),
            ],
        ),
    ]
