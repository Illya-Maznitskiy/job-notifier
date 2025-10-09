import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.user import get_user_by_telegram_id, create_user
from src.db.crud.user_keyword import upsert_user_keyword
from src.db.models.user import User
from src.db.models.job import Job
from logs.logger import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.telegram.bot_config import bot, ADMIN_ID


def get_keyboard(job: Job) -> InlineKeyboardMarkup:
    """Return inline keyboard with job.id in callback_data."""
    logger.info("-" * 60)
    logger.debug(f"Generating keyboard for job id={job.id}, title={job.title}")

    if not job or not hasattr(job, "id"):
        raise ValueError("Invalid job object")

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


async def notify_admin_startup() -> None:
    """Notify admin that the bot has started."""
    if ADMIN_ID:
        try:
            await bot.send_message(
                chat_id=ADMIN_ID, text="🚀 Bot has started and is ready!"
            )
            logger.info(f"Sent startup notification to admin {ADMIN_ID}")
        except Exception as e:
            logger.error(f"Failed to notify admin on startup: {e}")
    else:
        logger.warning("ADMIN_ID not set. Cannot notify admin on startup.")


def clean_short_title(title: str, max_words: int = 3) -> str:
    """Make title shorter."""
    if not title:
        return ""
    return " ".join(title.split()[:max_words])


def truncate_title(title: str, max_length: int = 100) -> str:
    """Truncate title without cutting words."""
    if not title:
        return ""
    words = title.split()
    truncated = ""
    for word in words:
        if len(truncated + (" " if truncated else "") + word) > max_length:
            break
        truncated += (" " if truncated else "") + word
    return truncated or title[:max_length]


def escape_markdown(text: str) -> str:
    """Escape Markdown special characters."""
    if not text:
        return ""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def get_job_id_by_url(session: AsyncSession, job_url: str) -> int | None:
    """Fetch job.id from DB using job.url."""
    if not job_url:
        return None
    try:
        result = await session.execute(
            select(Job.id).where(Job.url == job_url)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed fetching job id: {e}")
        return None


def create_vacancy_message(
    job: Job, score: int | None = None
) -> tuple[str, InlineKeyboardMarkup]:
    """Return vacancy message and keyboard."""
    if not job:
        raise ValueError("Invalid job object")

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
    session: AsyncSession, telegram_id: int, username: str | None = None
) -> User:
    """Return existing user or create new one."""
    if not telegram_id or not session:
        raise ValueError("Invalid telegram_id or session")

    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        return user
    if not username:
        username = telegram_id
        logger.info(
            f"User {telegram_id} doesn't have a username, "
            f"setting it to his telegram id {telegram_id}"
        )
    logger.info(
        f"Creating new user with id={telegram_id}, username={username}"
    )
    try:
        await bot.send_message(
            ADMIN_ID,
            f"New user joined 😉\nID: {telegram_id}\nUsername: {username}",
        )
    except Exception as e:
        logger.error(f"Failed notifying admin: {e}")

    return await create_user(session, telegram_id, username)


async def add_or_update_user_keyword(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    keyword: str,
    weight: int,
) -> str:
    """Add or update user's keyword rating."""
    if not telegram_id or not keyword:
        raise ValueError("Invalid user_id or keyword")

    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        user = await create_user(session, telegram_id, username)
        await session.commit()

    from src.db.crud.user_keyword import get_user_keyword

    existing_kw = await get_user_keyword(session, user.id, keyword)
    if existing_kw:
        existing_kw.weight = weight
        await session.flush()
        return "updated"

    await upsert_user_keyword(session, user.id, keyword, weight)
    return "created"
