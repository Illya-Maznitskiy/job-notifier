from aiogram import types
from aiogram.filters import StateFilter

from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)


@dp.message(
    StateFilter(None),
    lambda message: not (message.text and message.text.startswith("/")),
)
async def handle_random_text(message: types.Message) -> None:
    """Reply to non-command messages with tip."""
    logger.info("-" * 60)

    try:
        user_id = message.from_user.id
        text = message.text
        logger.info(f"User {user_id} sent random text: {text!r}")

        await message.answer(
            "Hey! Wrong number? Nah, just kidding. Tap /start to begin 😎"
        )
    except Exception as err:
        logger.exception(f"Failed handling random text: {err}")
