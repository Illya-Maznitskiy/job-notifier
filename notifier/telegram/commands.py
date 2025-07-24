import asyncio
import os
import random

from aiogram.filters import Command
from aiogram import types

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
    await send_vacancy_to_user(user_id)


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    """Stop the bot if user is admin."""
    logger.info("-" * 60)
    user_id = str(message.from_user.id)

    if user_id != os.getenv("ADMIN_ID"):
        logger.warning(f"Unauthorized stop attempt by user {user_id}")
        await message.answer("You are not allowed to stop the bot.")
        return

    logger.info(f"Admin {user_id} requested bot shutdown.")
    await message.answer("Bot is shutting down...")
    await bot.session.close()
    await dp.stop_polling()


@dp.message(
    lambda message: not (message.text and message.text.startswith("/"))
)
async def handle_random_text(message: types.Message):
    """Reply to random text with help info."""
    logger.info("-" * 60)
    user_id = message.from_user.id
    text = message.text
    logger.info(f"User {user_id} sent random text: {text!r}")

    help_text = (
        "Hi! I'm a job notifier bot 🤖\n\n"
        "Use the following commands:\n"
        "/start - Start interaction\n"
        "/next - Get next job vacancy\n"
        "/stop - Stop the bot (admin only)"
    )
    await message.answer(help_text)
