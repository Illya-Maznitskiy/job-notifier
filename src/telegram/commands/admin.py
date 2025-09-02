from aiogram.filters import Command
from aiogram import types


from logs.logger import logger
from src.telegram.bot_config import (
    dp,
    bot,
)
from src.telegram.job_utils import ADMIN_ID


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message) -> None:
    """Stop the bot if user is admin."""
    logger.info("-" * 60)
    user_id = str(message.from_user.id)

    if user_id != ADMIN_ID:
        logger.warning(f"Unauthorized stop attempt by user {user_id}")
        await message.answer("You are not allowed to stop the bot.")
        return

    logger.info(f"Admin {user_id} requested bot shutdown.")
    await message.answer("Bot is shutting down...")
    try:
        await bot.session.close()
        await dp.stop_polling()
    except Exception as e:
        logger.error(f"Error shutting down bot: {e}")
