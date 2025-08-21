import asyncio
import os
import random

from aiogram.filters import Command
from aiogram import types
from sqlalchemy import select

from db.crud.user import get_user_by_user_id
from db.crud.user_keyword import upsert_user_keyword
from db.db import AsyncSessionLocal
from db.models import UserKeyword, User
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


@dp.message(Command("add_keyword"))
async def add_keyword(message: types.Message):
    """Add or update a user keyword with a specified weight."""
    logger.info("-" * 60)
    user_id = message.from_user.id
    logger.info(
        f"User {user_id} invoked /add_keyword with text: {message.text!r}"
    )

    # Split text into exactly 3 parts: command, keyword, weight
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.answer(
            "Usage: /add_keyword <keyword> <weight>\nBoth are required ❌"
        )
        return

    keyword = parts[1].lower()
    try:
        weight = int(parts[2])
    except ValueError:
        await message.answer("Weight must be an integer ❌")
        return

    async with AsyncSessionLocal() as session:
        # Check if user exists
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to add a keyword."
            )
            await message.answer("You are not registered yet ❌")
            return

        # Check if keyword already exists
        from db.crud.user_keyword import get_user_keyword

        existing_kw = await get_user_keyword(session, user.id, keyword)
        if existing_kw:
            # Update existing keyword
            existing_kw.weight = weight
            await session.flush()
            action = "updated"
        else:
            # Create new keyword
            await upsert_user_keyword(session, user.id, keyword, weight)
            action = "created"

        await session.commit()

    logger.info(
        f"User {user_id} {action} keyword '{keyword}' with weight {weight}"
    )
    await message.answer(
        f"Keyword '{keyword}' {action} with weight {weight} ✅"
    )
