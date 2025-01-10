import asyncio
import os
import time

import telebot

from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)

CHAT_ID = -1002341988404


@bot.message_handler(commands=["get_id"])
def get_id(message):
    bot.send_message(message.chat.id, message.chat.id)


def get_text_about_overdue_borrowings():
    from borrowings_service.models import Borrowing

    max_length = 4096
    messages = []

    text = "Such borrows was overdue:\n"
    for borrow in Borrowing.objects.select_related("book", "user").filter(
        expected_return_datelte=timezone.now().date() - timezone.timedelta(days=1)
    ):
        if borrow:
            borrow_message = (
                f"Book: {borrow.book.title}\n"
                f"User email: {borrow.user.email}\n"
                f"Expected return date: {borrow.expected_return_date}\n"
                f"---------------------------------------\n"
            )

            if len(text + borrow_message) > max_length:
                messages.append(text)
                text = ""
            text += borrow_message

    messages.append(text)
    return messages


def send_notification_on_borrowing_overdue():

    messages = get_text_about_overdue_borrowings()

    if len(messages[0]) < 40:
        bot.send_message(CHAT_ID, "No borrowings overdue today!")
        time.sleep(0.25)
    else:
        for message in messages:
            bot.send_message(CHAT_ID, message)
            time.sleep(0.25)


def send_notification_on_success_payment(payment):
    text = (
        f"Payment was successfully completed:\n"
        f"Payment status:{payment.status}\n"
        f"User email: {payment.borrowing.user.email}\n"
        f"Money payed: {payment.money_to_pay}\n"
        f"Session id: {payment.session_id}\n"
    )
    bot.send_message(CHAT_ID, text)
    time.sleep(0.25)


async def poll():
    while True:
        try:
            await bot.polling(non_stop=True)
        except Exception as e:
            print(f"Error occurred: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(poll())