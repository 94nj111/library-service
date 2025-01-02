# Generated by Django 4.0.4 on 2025-01-02 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.CharField(
                        choices=[("HARD", "Hard"), ("SOFT", "Soft")], max_length=5
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
                ("daily_free", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
    ]
