import asyncio
import os
import sqlite3
import time
from datetime import datetime

import telebot
from celery import shared_task

from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)


@shared_task
def save_user(user_id):
    with sqlite3.connect("../subscribers.db") as db:
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
        db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        db.commit()


@shared_task
def get_users():
    with sqlite3.connect("../subscribers.db") as db:
        cursor = db.execute("SELECT id FROM users")
        return [row[0] for row in cursor]


@shared_task
@bot.message_handler(commands=["start"])
def send_welcome(message):
    text = (
        "Greetings, I'm a library bot and from now on I'll be sending you notifications about: \n"
        " - new borrowing created, \n - borrowings overdue \n - successful payments"
    )

    if message.chat.id:
        bot.send_message(message.chat.id, text=text)
        save_user(message.chat.id)
    else:
        bot.send_message(message.from_user.id, text=text)
        save_user(message.from_user.id)


def get_text_about_overdue_borrowings():
    from borrowings_service.models import Borrowing

    max_length = 4096
    messages = []

    text = "Such borrows was overdue:\n"
    for borrow in Borrowing.objects.select_related("book", "user").filter(
        expected_return_date__lte=timezone.now().date() - timezone.timedelta(days=1)
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
    user_ids = get_users()

    messages = get_text_about_overdue_borrowings()

    if len(messages[0]) < 40:
        for user_id in user_ids:
            bot.send_message(user_id, "No borrowings overdue today!")
            time.sleep(0.25)
    else:
        for user_id in user_ids:
            for message in messages:
                bot.send_message(user_id, message)
                time.sleep(0.25)


@shared_task
def send_notification_on_success_payment(payment):
    user_ids = get_users()
    text = (f"Payment was successfully completed:\n"
            f"Payment status:{payment.status}\n"
            f"User email: {payment.borrowing.user.email}\n"
            f"Money payed: {payment.money_to_pay}\n"
            f"Session id: {payment.session_id}\n")
    for user_id in user_ids:
        bot.send_message(user_id, text)
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
