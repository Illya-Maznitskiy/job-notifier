import hashlib
import json
import os
import re

from logs.logger import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from notifier.telegram.bot_config import bot, job_id_map


def save_applied(applied_jobs, path):
    """Save applied jobs data to JSON file."""
    logger.info("-" * 60)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(applied_jobs, f, indent=2, ensure_ascii=False)

    total_applied = sum(
        len(user_data["jobs"]) for user_data in applied_jobs.values()
    )
    logger.info(
        f"Applied jobs saved. Total applied jobs count: {total_applied}"
    )


def save_skipped(skipped_jobs, path):
    """Save skipped jobs data to JSON file."""
    logger.info("-" * 60)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(skipped_jobs, f, indent=2, ensure_ascii=False)

    total_skipped = sum(
        len(user_data["jobs"]) for user_data in skipped_jobs.values()
    )
    logger.info(
        f"Skipped jobs saved. Total skipped jobs count: {total_skipped}"
    )


def find_job_by_url(job_url, filtered_file_path):
    """Find job in file by its URL."""
    logger.info("-" * 60)
    logger.info(f"Looking for job with URL: {job_url}")

    with open(filtered_file_path, "r", encoding="utf-8") as f:
        all_jobs = json.load(f)
        for job in all_jobs:
            if job.get("url") == job_url:
                logger.info(
                    f"Job found: {job.get('title', 'Unknown Title')} | {job.get('company', 'Unknown Company')}"
                )
                return job

    logger.warning(f"No job found for URL: {job_url}")
    return None


def get_keyboard(title: str, job_url: str) -> InlineKeyboardMarkup:
    """Return inline keyboard with correct job URL."""
    logger.info("-" * 60)
    logger.debug(f"Generating keyboard with URL: {job_url} for title: {title}")

    job_id = get_job_id(job_url)
    job_id_map[job_id] = job_url

    def get_callback_data(action):
        return f"{action}|{job_id}"

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


def escape_markdown(text: str) -> str:
    """Remove all asterisk (*) characters to prevent Markdown errors."""
    return re.sub(r"\*", "", text)


def get_job_id(job_url: str) -> str:
    """Create short unique ID to fit Telegram callback_data limit."""
    return hashlib.md5(job_url.encode()).hexdigest()[:8]


def create_vacancy_message(job: dict) -> tuple[str, object]:
    """
    Create the formatted vacancy message and keyboard for a job.
    """
    url = job.get("url", "")
    keyboard = get_keyboard(job["title"], url)  # pass URL here

    # Extract values with sensible defaults
    company = job.get("company", "Unknown")
    score = job.get("score", "No score")
    job_title = escape_markdown(truncate_title(job.get("title", "No Title")))

    # Create Markdown-safe message
    url_text = f"[🔗 View Job Posting]({url})" if url else "No URL provided"

    msg = (
        f"🔹 *{job_title}*\n\n"
        f"🏢 {company}\n"
        f"📊 Score: {score}\n\n\n"
        f"{url_text}"
    )

    return msg, keyboard
