from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from sqlalchemy import select

from src.db.db import AsyncSessionLocal
from logs.logger import logger
from src.db.models.user_region import UserRegion
from src.telegram.bot_config import (
    dp,
)
from src.telegram.job_utils import (
    get_or_create_user,
)


class RegionStates(StatesGroup):
    """Add region conversation states."""

    waiting_for_region: State = State()


@dp.message(Command("region"))
async def add_region_start(message: Message, state: FSMContext) -> None:
    """Start adding region conversation."""
    telegram_id = message.from_user.id

    logger.info("-" * 60)
    logger.info(f"User {telegram_id} started adding region")

    logger.info(f"Cleared previous state for user {telegram_id}")
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ukraine", callback_data="region_Ukraine"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Poland", callback_data="region_Poland"
                )
            ],
            [InlineKeyboardButton(text="All", callback_data="region_all")],
        ]
    )
    await message.answer(
        "Choose your region for job search 🌍",
        reply_markup=keyboard,
    )
    await state.set_state(RegionStates.waiting_for_region)


@dp.callback_query(StateFilter(RegionStates.waiting_for_region))
async def process_region_selection(
    cb: CallbackQuery, state: FSMContext
) -> None:
    """Set user's  region."""
    region: str = cb.data.split("_")[1]
    user_id: int = cb.from_user.id

    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session, user_id, cb.from_user.username
            )

            existing = await session.execute(
                select(UserRegion).where(UserRegion.user_id == user.id)
            )
            for r in existing.scalars().all():
                await session.delete(r)

            session.add(UserRegion(user_id=user.id, region=region))
            await session.commit()

        await cb.message.answer(f"Region set to {region} ✅")

    except Exception as e:
        logger.error(f"Failed to set region for {user_id}: {e}")
        await cb.message.answer("Something went wrong ❌")

    await state.clear()
    await cb.answer()
