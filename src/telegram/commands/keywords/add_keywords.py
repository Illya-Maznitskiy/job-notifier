from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.telegram.bot_config import (
    dp,
)
from src.telegram.commands.keywords.utils import parse_keywords
from src.telegram.job_utils import add_or_update_user_keyword


class AddKeywordStates(StatesGroup):
    """Add keyword conversation states."""

    waiting_for_keyword: State = State()
    waiting_for_weight: State = State()


@dp.message(Command("add"))
async def add_keyword_start(message: Message, state: FSMContext) -> None:
    """Start adding keyword conversation."""
    if not message or not state:
        logger.error("Message or state is None")
        return

    user_id = message.from_user.id
    logger.info("-" * 60)
    logger.info(f"User {user_id} started adding keyword")
    await message.answer(
        "Send me a keyword\nI'll use it to find jobs for you ✅"
    )
    await message.answer(
        "Example: Python\n💡You can also try: SQL, Junior, or any skill"
    )
    await state.set_state(AddKeywordStates.waiting_for_keyword)


@dp.message(StateFilter(AddKeywordStates.waiting_for_keyword))
async def add_keyword_receive(message: Message, state: FSMContext) -> None:
    """Receive keyword from user."""
    if not message.text:
        logger.warning("Received empty keyword")
        return

    keywords = parse_keywords(message.text)
    logger.info(f"Processed keywords: {keywords}")

    await state.update_data(keywords=keywords)

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
            [
                InlineKeyboardButton(
                    text="❓ Info", callback_data="how_it_works"
                )
            ],
        ]
    )
    await message.answer(
        f"Choose a score for '{keywords}':\n💡Feel free to use custom and "
        f"negative values like -10, 5 ...",
        reply_markup=keyboard,
    )


@dp.message(StateFilter(AddKeywordStates.waiting_for_weight))
async def add_keyword_save(message: Message, state: FSMContext) -> None:
    """Save multiple keywords and weight in DB."""
    user_id = message.from_user.id
    data = await state.get_data()
    keywords = data["keywords"]

    try:
        weight = int(message.text)
    except ValueError:
        weight = 10  # default

    async with AsyncSessionLocal() as session:
        for keyword in keywords:
            action = await add_or_update_user_keyword(
                session=session,
                user_id=user_id,
                username=str(message.from_user.username),
                keyword=keyword,
                weight=weight,
            )
            await session.commit()

            logger.info(
                f"User {user_id} {action} keyword '{keyword}'"
                f" with weight {weight}"
            )

            await message.answer(
                f"Keyword '{keyword}' {action} with score {weight} ✅"
            )

    await message.answer("You can use /refresh now to filter jobs for you 😎")
    await state.clear()


@dp.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("weight_")
)
async def process_weight_callback(
    cb: CallbackQuery, state: FSMContext
) -> None:
    """Handle weight selection buttons."""

    if cb.data == "weight_custom":
        await cb.message.answer("Send the weight number you want ➡️")
        await state.set_state(AddKeywordStates.waiting_for_weight)
        await cb.answer()
        return

    # Extract weight from callback data
    weight = int(cb.data.split("_")[1])
    data = await state.get_data()
    keywords = data["keywords"]

    async with AsyncSessionLocal() as session:
        for keyword in keywords:
            action = await add_or_update_user_keyword(
                session=session,
                user_id=cb.from_user.id,
                username=str(cb.from_user.username),
                keyword=keyword,
                weight=weight,
            )
            await session.commit()

            logger.info(
                f"User {cb.from_user.id} {action} keyword '{keyword}' "
                f"with weight {weight}"
            )

            await cb.message.answer(
                f"Keyword '{keyword}' {action} with score {weight} ✅"
            )

    await cb.message.answer(
        "You can use /refresh now to filter jobs for you 😎"
    )
    await state.clear()
    await cb.answer()


@dp.callback_query(lambda c: c.data == "how_it_works")
async def process_how_it_works(cb: CallbackQuery) -> None:
    """Explain briefly how keyword scoring works."""
    if not cb.message:
        await cb.answer("Message not available")
        return

    text = (
        "• Add a keyword and score (e.g., JS → 10)\n"
        "• I scan each job titles/skills and update scores\n"
        "• Then I show the top jobs for you\n\n"
        "That’s all! 😎"
    )
    await cb.message.answer(text)
    await cb.answer()
