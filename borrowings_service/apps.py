from django.apps import AppConfig


class BorrowingsServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings_service"

    def ready(self):
        import borrowings_service.signals  # noqa
        import library_bot.celery_app # noqa
