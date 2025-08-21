import asyncio
import random

from aiogram.filters import Command
from aiogram import types

from db.db import AsyncSessionLocal
from logs.logger import logger
from notifier.telegram.jobs import send_vacancy_to_user
from notifier.telegram.bot_config import (
    dp,
    bot,
    READY_GIF_URLS,
)


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    """Greet user and introduce the bot."""
    logger.info("-" * 60)
    logger.info(f"User {message.from_user.id} started the bot.")
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

    # Optional: small pause for dramatic effect
    await asyncio.sleep(2)

    # Then send the vacancy
    async with AsyncSessionLocal() as session:
        await send_vacancy_to_user(user_id, session, user_id)
