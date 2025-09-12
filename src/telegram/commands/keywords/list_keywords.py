from aiogram.filters import Command
from aiogram import types


from src.db.crud.user import get_user_by_user_id
from src.db.crud.user_keyword import get_user_all_keywords
from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)


@dp.message(Command("keywords"))
async def list_keywords(message: types.Message) -> None:
    """List all keywords for the current user."""
    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(f"User {user_id} invoked /list_keywords")

    async with AsyncSessionLocal() as session:
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to list keywords."
            )
            logger.warning(
                f"Unregistered user {user_id} message: {message.text}"
            )
            await message.answer(
                "Telegram rules say you need to hit"
                " /start first 🤷‍♂️ Rules are rules!"
            )
            return

        keywords = await get_user_all_keywords(session, user.id)

        if not keywords:
            await message.answer("You haven't added any keywords yet ❌")
            return

        reply = "🗝️ Your keywords:\n\n"
        for kw in keywords:
            reply += f"• {kw.keyword} ({kw.weight})\n"

        await message.answer(reply)
