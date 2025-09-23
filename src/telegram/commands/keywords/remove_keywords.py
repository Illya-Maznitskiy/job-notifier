from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message
from aiogram.fsm.state import StatesGroup, State

from src.db.crud.user import get_user_by_telegram_id
from src.db.crud.user_keyword import get_user_all_keywords
from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)
from src.telegram.commands.keywords.utils import parse_keywords
from src.db.crud.user_keyword import delete_user_keyword


class RemoveKeywordStates(StatesGroup):
    """Remove keyword conversation states."""

    waiting_for_keyword: State = State()


@dp.message(Command("remove"))
async def remove_keyword(message: Message, state: FSMContext) -> None:
    """Remove one or multiple keywords for the current user."""
    if not message or not state:
        logger.error("Message or state is None")
        return

    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, user_id)
        user_keywords = await get_user_all_keywords(
            session, user.id  # type: ignore
        )

        if not user_keywords:
            await message.answer("You have no keywords to remove 🤷‍♂️😺")
            logger.error("User has no keywords")
            return

    logger.info("-" * 60)
    logger.info(f"User {user_id} invoked /remove with text: {message.text!r}")

    await message.answer("Send me a keyword from your keywords 🧹")

    reply = "\n".join(f"• {kw.keyword}" for kw in user_keywords)
    await message.answer(reply)

    await state.set_state(RemoveKeywordStates.waiting_for_keyword)


@dp.message(StateFilter(RemoveKeywordStates.waiting_for_keyword))
async def remove_keyword_receive(message: Message, state: FSMContext) -> None:
    if message.text.startswith("/"):
        logger.info(
            f"RemoveKeyword FSM stopped by new command: {message.text!r} "
            f"from user {message.from_user.id}"
        )
        await state.clear()
        return

    user_id = message.from_user.id
    keywords = parse_keywords(message.text)

    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to remove keywords."
            )
            await message.answer("Hmm, system issue 🤷‍♂️")
            return

        removed, not_found = [], []
        for kw in keywords:
            deleted = await delete_user_keyword(session, user.id, kw)
            if deleted:
                removed.append(kw)
            else:
                not_found.append(kw)
        await session.commit()

    if removed:
        logger.info(f"Removed {len(removed)} keywords")
        await message.answer(f"💅 Successfully removed: {', '.join(removed)}")
        await message.answer(
            "Use /refresh to filter jobs without that keyword 🕵️‍♂️"
        )
    if not_found:
        logger.info(f"Not found {len(not_found)} keywords")
        await message.answer(f"Can't find: {', '.join(not_found)} 👀")
        await message.answer("🕶️ You can try again /remove")
    await state.clear()
