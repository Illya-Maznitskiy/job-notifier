from aiogram.filters import Command, StateFilter
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from src.db.crud.user import get_user_by_user_id
from src.db.crud.user_keyword import get_user_all_keywords
from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)
from src.telegram.job_utils import add_or_update_user_keyword


class AddKeywordStates(StatesGroup):
    """States for adding a keyword conversation flow."""

    waiting_for_keyword: State = State()  # Waiting user to send keyword
    waiting_for_weight: State = State()  # Waiting user to send weight


@dp.message(Command("add_keyword"))
async def add_keyword_start(message: Message, state: FSMContext):
    """Start adding keyword conversation."""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started adding keyword")
    await message.answer(
        f"Send me a keyword\nI'll use it to find jobs for you ✅"
    )
    await message.answer("Example: Python")
    await state.set_state(AddKeywordStates.waiting_for_keyword)


@dp.message(StateFilter(AddKeywordStates.waiting_for_keyword))
async def add_keyword_receive(message: Message, state: FSMContext):
    """Receive keyword from user."""
    await state.update_data(keyword=message.text.lower())
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Default (10)", callback_data="weight_10"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Custom", callback_data="weight_custom"
                )
            ],
        ]
    )
    await message.answer("Choose a weight:", reply_markup=keyboard)


@dp.message(StateFilter(AddKeywordStates.waiting_for_weight))
async def add_keyword_save(message: Message, state: FSMContext):
    """Save keyword and weight in DB."""
    user_id = message.from_user.id
    data = await state.get_data()
    keyword = data["keyword"]

    try:
        weight = int(message.text)
    except ValueError:
        weight = 10  # default

    async with AsyncSessionLocal() as session:
        action = await add_or_update_user_keyword(
            session=session,
            user_id=message.from_user.id,
            username=str(message.from_user.username),
            keyword=keyword,
            weight=weight,
        )
        await session.commit()

    logger.info(
        f"User {user_id} {action} keyword '{keyword}' with weight {weight}"
    )
    await message.answer(
        f"Keyword '{keyword}' {action} with weight {weight} ✅"
    )
    await message.answer("You can use /refresh now to filter jobs for you 😎")
    await state.clear()


@dp.message(Command("list_keywords"))
async def list_keywords(message: types.Message):
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
            await message.answer("You are not registered yet ❌")
            return

        keywords = await get_user_all_keywords(session, user.id)

        if not keywords:
            await message.answer("You haven't added any keywords yet ❌")
            return

        reply = "🗝️ Your keywords:\n\n"
        for kw in keywords:
            reply += f"• {kw.keyword} ({kw.weight})\n"

        await message.answer(reply)


@dp.message(Command("remove_keyword"))
async def remove_keyword(message: types.Message):
    """Remove a keyword for the current user."""
    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(
        f"User {user_id} invoked /remove_keyword with text: {message.text!r}"
    )

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /remove_keyword <keyword> ❌")
        return

    keyword = parts[1].lower()

    async with AsyncSessionLocal() as session:
        # Check if user exists
        user = await get_user_by_user_id(session, user_id)
        if not user:
            logger.warning(
                f"Unregistered user {user_id} tried to remove a keyword."
            )
            await message.answer("You are not registered yet ❌")
            return

        # Try to delete keyword
        from src.db.crud.user_keyword import delete_user_keyword

        deleted = await delete_user_keyword(session, user.id, keyword)

        if deleted:
            await session.commit()
            await message.answer(f"Keyword '{keyword}' removed ✅")
            logger.info(f"User {user_id} removed keyword '{keyword}'")
        else:
            await message.answer(f"Keyword '{keyword}' not found ❌")
            logger.info(
                f"User {user_id} tried to remove non-existent keyword '{keyword}'"
            )


@dp.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("weight_")
)
async def process_weight_callback(cb: CallbackQuery, state: FSMContext):
    """Handle weight selection buttons."""

    if cb.data == "weight_custom":
        await cb.message.answer("Send the weight number you want ➡️")
        await state.set_state(AddKeywordStates.waiting_for_weight)
        await cb.answer()
        return

    # Extract weight from callback data
    weight = int(cb.data.split("_")[1])
    data = await state.get_data()
    keyword = data["keyword"]

    # Save keyword in DB (you can reuse the DB part from add_keyword_save)
    async with AsyncSessionLocal() as session:
        action = await add_or_update_user_keyword(
            session=session,
            user_id=cb.from_user.id,
            username=str(cb.from_user.username),
            keyword=keyword,
            weight=weight,
        )
        await session.commit()

    await cb.message.answer(
        f"Keyword '{keyword}' {action} with weight {weight} ✅"
    )
    await cb.message.answer(
        "You can use /refresh now to filter jobs for you 😎"
    )

    await state.clear()
    await cb.answer()
