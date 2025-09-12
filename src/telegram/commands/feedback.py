from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from src.telegram.bot_config import dp, bot
from src.telegram.job_utils import ADMIN_ID
from logs.logger import logger


class SendFeedbackStates(StatesGroup):
    """Send feedback states."""

    waiting_for_feedback: State = State()


@dp.message(Command("feedback"))
async def feedback_start(message: Message, state: FSMContext) -> None:
    """Start feedback conversation."""
    await message.answer("Please type your feedback 🌟")
    await state.set_state(SendFeedbackStates.waiting_for_feedback)


@dp.message(StateFilter(SendFeedbackStates.waiting_for_feedback))
async def feedback_receive(message: Message, state: FSMContext) -> None:
    """Receive feedback and send to admin."""
    text = message.text
    try:
        await bot.send_message(
            ADMIN_ID,
            f"👤 Feedback from @{message.from_user.username} "
            f"({message.from_user.id}):\n{text}",
        )
        await message.answer("💌 Thanks! Your feedback has been sent.")
    except Exception as e:
        logger.error(f"Failed to send feedback: {e}")
        await message.answer("❌ Failed to send feedback, try later.")
    finally:
        await state.clear()
