from django.contrib import admin

from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "book",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "is_active",
    )

    list_filter = ("user", "borrow_date", "actual_return_date", "book")

    ordering = ("-borrow_date", "expected_return_date")

    search_fields = ("user__email", "book__title")

    readonly_fields = ("is_active",)

    def is_active(self, obj):
        return obj.is_active

    is_active.boolean = True
