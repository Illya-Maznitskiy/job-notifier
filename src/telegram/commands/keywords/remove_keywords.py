import re

from aiogram.filters import Command
from aiogram import types

from src.db.crud.user import get_user_by_user_id
from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)


@dp.message(Command("remove"))
async def remove_keyword(message: types.Message) -> None:
    """Remove one or multiple keywords for the current user."""
    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(f"User {user_id} invoked /remove with text: {message.text!r}")

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /remove <keyword> ❌")
        await message.answer("💡 Example: /remove python, sql")
        return

    # normalize like /add
    keywords = [
        k.strip().lower() for k in re.split(r"[, ]+", parts[1]) if k.strip()
    ]
    logger.info(f"Processed keywords to remove: {keywords}")

    async with AsyncSessionLocal() as session:
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to remove keywords."
            )
            await message.answer("Hmm, system issue 🤷‍♂️")
            return

        from src.db.crud.user_keyword import delete_user_keyword

        removed = []
        not_found = []
        for keyword in keywords:
            deleted = await delete_user_keyword(session, user.id, keyword)
            if deleted:
                removed.append(keyword)
            else:
                not_found.append(keyword)
        await session.commit()

        if removed:
            await message.answer(f"Removed: {', '.join(removed)} ✅")
        if not_found:
            await message.answer(f"Not found: {', '.join(not_found)} ❌")

        logger.info(
            f"User {user_id} removed: {removed}, tried not found: {not_found}"
        )
