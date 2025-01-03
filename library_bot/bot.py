import asyncio
import os

import aiosqlite
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

TOKEN = os.environ.get("TOKEN")

bot = AsyncTeleBot(TOKEN)


async def save_user(user_id):
    async with aiosqlite.connect("../subscribers.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()


async def get_users():
    async with aiosqlite.connect("../subscribers.db") as db:
        async with db.execute("SELECT id FROM users") as cursor:
            return [row[0] async for row in cursor]


@bot.message_handler(commands=["start"])
async def send_welcome(message):
    text = (
        "Greetings, I'm a library bot and from now on I'll be sending you notifications about: \n"
        " - new borrowing created, \n - borrowings overdue \n - successful payments"
    )

    if message.chat.id:
        await bot.send_message(message.chat.id, text=text)
        await save_user(message.chat.id)
    else:
        await bot.send_message(message.from_user.id, text=text)
        await save_user(message.from_user.id)


if __name__ == "__main__":
    asyncio.run(bot.polling())
