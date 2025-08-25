from aiogram import types


from logs.logger import logger
from src.notifier.telegram.bot_config import (
    dp,
)


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
