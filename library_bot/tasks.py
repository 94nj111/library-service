from celery import shared_task

from library_bot.bot import send_notification_on_borrowing_overdue


@shared_task
def check_overdue():
    return send_notification_on_borrowing_overdue()
