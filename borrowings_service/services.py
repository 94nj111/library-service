from rest_framework.exceptions import ValidationError


def validate_user_payments(request):
    user = request.user

    borrowings = user.borrowings.all()

    for borrowing in borrowings:
        payments = borrowing.payments.filter(status="PENDING")
        if payments.exists():
            raise ValidationError("You have unpaid bills")
