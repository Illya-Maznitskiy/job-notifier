import os
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.user import get_user_by_user_id, create_user
from src.db.models import User, Job
from logs.logger import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.telegram.bot_config import bot


def get_keyboard(job: Job) -> InlineKeyboardMarkup:
    """Return inline keyboard with job.id in callback_data."""
    logger.info("-" * 60)
    logger.debug(f"Generating keyboard for job id={job.id}, title={job.title}")

    def get_callback_data(action: str) -> str:
        return f"{action}|{job.id}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Applied ✅",
                    callback_data=get_callback_data("applied"),
                ),
                InlineKeyboardButton(
                    text="Skip ⏭️",
                    callback_data=get_callback_data("skip"),
                ),
            ]
        ]
    )


async def notify_admin_startup():
    """Notify admin that the bot has started."""
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        try:
            await bot.send_message(
                chat_id=admin_id, text="🚀 Bot has started and is ready!"
            )
            logger.info(f"Sent startup notification to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to notify admin on startup: {e}")
    else:
        logger.warning("ADMIN_ID not set. Cannot notify admin on startup.")


def clean_short_title(title: str, max_words=3):
    """Make title shorter."""
    words = title.split()
    return " ".join(words[:max_words])


def truncate_title(title: str, max_length: int = 34) -> str:
    """Truncate title without cutting words."""
    words = title.split()
    truncated = ""
    for word in words:
        if len(truncated + " " + word if truncated else word) > max_length:
            break
        truncated += (" " if truncated else "") + word
    return truncated or title[:max_length]


def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


# def get_job_id(job_url: str) -> str:
#     """Create short unique ID to fit Telegram callback_data limit."""
#     return hashlib.md5(job_url.encode()).hexdigest()[:8]


async def get_job_id_by_url(session: AsyncSession, job_url: str) -> int | None:
    """Fetch job.id from DB using job.url."""
    result = await session.execute(select(Job.id).where(Job.url == job_url))
    return result.scalar_one_or_none()


def create_vacancy_message(
    job: Job, score: int | None = None
) -> tuple[str, object]:
    """
    Create the formatted vacancy message and keyboard for a job.
    """
    url = job.url or ""
    keyboard = get_keyboard(job)

    company = escape_markdown(job.company or "Unknown")
    job_title = escape_markdown(truncate_title(job.title or "No Title"))
    score_text = score if score is not None else "No score"

    url_text = f"[🔗 View Job Posting]({url})" if url else "No URL provided"

    msg = (
        f"🔹 *{job_title}*\n\n"
        f"🏢 {company}\n"
        f"📊 Score: {score_text}\n\n\n"
        f"{url_text}"
    )

    return msg, keyboard


async def get_or_create_user(
    session: AsyncSession, user_id: int, username: str | None = None
) -> User:
    """Fetch user or create if not exists in database."""
    user = await get_user_by_user_id(session, user_id)  # try to get user
    if user:
        return user  # return existing user
    return await create_user(
        session, user_id, username
    )  # create new if not found
