import random
from datetime import date

from aiogram.filters import Command
from aiogram import types

from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.job_utils import get_or_create_user
from src.telegram.jobs import send_vacancy_to_user
from src.telegram.bot_config import (
    dp,
    bot,
    READY_GIF_URLS,
)


MAX_VACANCIES_PER_DAY = 7


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message) -> None:
    """Greet user and introduce the bot."""
    logger.info("-" * 60)
    telegram_id = message.from_user.id
    logger.info(f"User {telegram_id} started the bot.")

    try:
        await message.answer(
            "Hi! I'll send you new IT jobs. Use /add to unlock jobs 😉"
        )
        logger.info(f"Hi message was sent to {telegram_id}")
    except Exception as e:
        logger.error(f"Error in /start for user {telegram_id}: {e}")
        await message.answer("⚠️ Something went wrong. Please try again.")


@dp.message(Command(commands=["vacancy"]))
async def send_next_vacancy(message: types.Message) -> None:
    """Send next job vacancy to the user."""
    logger.info("-" * 60)
    telegram_id = message.from_user.id
    logger.info(f"User {telegram_id} requested next vacancy.")

    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session,
                telegram_id,
                username=message.from_user.username,
            )

            if user.last_reset_date < date.today():
                user.refresh_count = 0
                user.vacancies_count = 0
                user.last_reset_date = date.today()
                await session.commit()

            if user.vacancies_count >= MAX_VACANCIES_PER_DAY:
                await message.answer(
                    f"⚡ {MAX_VACANCIES_PER_DAY} jobs done today!"
                )
                await message.answer("Support the bot for future updates 💎")
                return

            user.vacancies_count += 1
            await session.commit()

            gif_url = random.choice(READY_GIF_URLS)
            await bot.send_animation(
                chat_id=message.chat.id,
                animation=gif_url,
                caption="Are you ready?! 🔥\n(Applied and Skip buttons are just "
                "to track vacancies in DB for now)",
            )
            await send_vacancy_to_user(
                str(telegram_id), session, str(telegram_id)
            )
    except Exception as e:
        logger.error(f"Error sending vacancy to user {telegram_id}: {e}")
        await message.answer("Server error. Try again later 🤷‍♂️")
