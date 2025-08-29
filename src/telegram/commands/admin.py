import os

from aiogram.filters import Command
from aiogram import types


from logs.logger import logger
from src.telegram.bot_config import (
    dp,
    bot,
)


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
