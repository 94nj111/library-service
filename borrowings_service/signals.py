from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowings_service.models import Borrowing


@receiver(post_save, sender=Borrowing)
async def send_notification_on_borrowing_created(sender, instance, created, **kwargs):
    if created:
        from library_bot.bot import bot, get_users

        borrow_date = datetime.strftime(instance.borrow_date, "%Y-%m-%d %H:%M:%S")
        text = (
            f"New borrowing was created:\n"
            f"Borrow date: {borrow_date}\n"
            f"Expected return date: {instance.expected_return_date}\n"
            f"Book: {instance.book.title}\n"
            f"User email: {instance.user.email}"
        )

        for user_id in await get_users():
            await bot.send_message(user_id, text)
