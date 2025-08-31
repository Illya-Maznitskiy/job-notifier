from aiogram import types
from aiogram.filters import Command

from src.telegram.bot_config import dp, bot
from src.telegram.job_utils import ADMIN_ID
from logs.logger import logger


@dp.message(Command(commands=["feedback"]))
async def feedback_cmd(message: types.Message):
    """Send user feedback directly to admin via /feedback command."""
    logger.info("-" * 60)

    # Get everything after /feedback
    text = message.text
    if text:
        # Remove the command part
        parts = text.split(maxsplit=1)
        text = parts[1] if len(parts) > 1 else None

    if not text:
        await message.reply(
            "🕵️ Please send your feedback after the command, e.g., /feedback I love this bot!"
        )
        logger.info(
            f"User {message.from_user.id} tried /feedback with no text."
        )
        return

    logger.info(f"User {message.from_user.id} sent feedback: {text}")

    try:
        await bot.send_message(
            ADMIN_ID,
            f"👤 Feedback from @{message.from_user.username} ({message.from_user.id}):\n{text}",
        )
        await message.reply("💌 Thanks! Your feedback has been sent")
        logger.info(
            f"Feedback successfully sent to admin from {message.from_user.id}."
        )
    except Exception as e:
        logger.error(
            f"Failed to send feedback from {message.from_user.id}: {e}"
        )
        await message.reply("Oops, something went wrong. Try again later.")
