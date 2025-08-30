import asyncio
import random
from datetime import timedelta, datetime

from aiogram.filters import Command
from aiogram import types

from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.jobs import send_vacancy_to_user
from src.telegram.bot_config import (
    dp,
    bot,
    READY_GIF_URLS,
)


last_start = {}
COOLDOWN = timedelta(seconds=30)


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    """Greet user and introduce the bot."""
    logger.info("-" * 60)
    logger.info(f"User {message.from_user.id} started the bot.")

    user_id = message.from_user.id
    now = datetime.now()

    if user_id in last_start and now - last_start[user_id] < COOLDOWN:
        return  # ignore repeated /start

    last_start[user_id] = now
    await message.answer(
        "Hi! I'll send you new dev jobs. Use /next to get a vacancy 😉"
    )


@dp.message(Command(commands=["next"]))
async def send_next_vacancy(message: types.Message):
    """Send next job vacancy to the user."""
    logger.info("-" * 60)
    user_id = str(message.from_user.id)
    logger.info(f"User {user_id} requested next vacancy.")

    # Choose a random GIF from the list
    gif_url = random.choice(READY_GIF_URLS)

    # Send the "Are you ready?!" GIF
    await bot.send_animation(
        chat_id=message.chat.id,
        animation=gif_url,
        caption="Are you ready?! 🔥",
    )

    # Then send the vacancy
    async with AsyncSessionLocal() as session:
        await send_vacancy_to_user(user_id, session, user_id)
