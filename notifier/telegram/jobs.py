import json
import random
from datetime import datetime

from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from .bot_config import (
    bot,
    dp,
    FILTERED_FILE,
    applied_jobs,
    skipped_jobs,
    SKIPPED_FILE,
    APPLIED_FILE,
    user_request_count,
    MEME_GIFS,
)
from logs.logger import logger
from notifier.telegram.job_utils import (
    save_applied,
    save_skipped,
    clean_short_title,
    create_vacancy_message,
    find_job_by_url,
)


async def send_vacancy_to_user(user_id: str):
    """Send next unviewed vacancy to the user."""
    logger.info("-" * 60)
    logger.info(f"Sending vacancy to user: {user_id}")

    if not FILTERED_FILE.exists():
        logger.warning("Filtered file not found.")
        await bot.send_message(user_id, "No vacancies found yet.")
        return

    with open(FILTERED_FILE, "r", encoding="utf-8") as f:
        vacancies = json.load(f)

    user_applied = applied_jobs.get(user_id, {}).get("jobs", [])
    user_skipped = skipped_jobs.get(user_id, {}).get("jobs", [])
    applied_urls = {entry["url"] for entry in user_applied}
    skipped_urls = {entry["url"] for entry in user_skipped}

    for job in vacancies:
        job_url = job["url"]
        if job_url not in applied_urls and job_url not in skipped_urls:
            msg, keyboard = create_vacancy_message(job)
            await bot.send_message(
                user_id, msg, reply_markup=keyboard, parse_mode="Markdown"
            )
            logger.info(f"Sent vacancy {job_url} to user {user_id}")
            return

    logger.info(f"No new vacancies for user {user_id}")
    await bot.send_message(user_id, "🫠 Dried up. Jobs gone. I am but dust")


@dp.callback_query(
    lambda c: c.data and c.data.startswith(("applied|", "skip|"))
)
async def process_callback(callback_query: types.CallbackQuery):
    """Handle user 'applied' or 'skip' button clicks."""
    logger.info("-" * 60)

    action, job_url = callback_query.data.split("|", 1)
    job = find_job_by_url(job_url, FILTERED_FILE)
    user_id = str(callback_query.from_user.id)
    logger.info(f"Callback from user {user_id}: {action}")

    if not job:
        logger.warning(f"Job not found for hash: {job_url}")
        try:
            await bot.answer_callback_query(
                callback_query.id, text="Job not found."
            )
        except TelegramBadRequest as e:
            if "query is too old" in str(e):
                logger.warning("Callback query expired for 'Job not found'.")
            else:
                raise
        return

    title = job["title"]
    job_url = job["url"]
    now_str = datetime.utcnow().isoformat()

    job_data = {
        "url": job_url,
        "datetime": now_str,
    }
    logger.info(f"User {user_id} marked job '{title}' as '{action}'")

    if action == "applied":
        user_data = applied_jobs.setdefault(
            user_id,
            {"username": callback_query.from_user.username, "jobs": []},
        )
        user_data["username"] = (
            callback_query.from_user.username
        )  # keep username updated
        user_data["jobs"].append(job_data)

        save_applied(applied_jobs, APPLIED_FILE)

        try:
            await bot.answer_callback_query(
                callback_query.id, text="Marked as applied!"
            )
        except TelegramBadRequest as e:
            if "query is too old" in str(e):
                logger.warning("Callback query expired, ignoring.")
            else:
                raise
        short_title = clean_short_title(title)
        await bot.send_message(
            user_id, f"Marked '{short_title}' as applied 😎"
        )
        # Increment request count
        user_request_count[user_id] += 1

        # After every 3 requests, send a meme
        if user_request_count[user_id] % 3 == 0:
            meme_url = random.choice(MEME_GIFS)
            await callback_query.message.answer_animation(meme_url)
            logger.info(f"Sent meme to user {user_id}")

    elif action == "skip":
        user_data = skipped_jobs.setdefault(
            user_id,
            {"username": callback_query.from_user.username, "jobs": []},
        )
        user_data["username"] = callback_query.from_user.username
        user_data["jobs"].append(job_data)
        save_skipped(skipped_jobs, SKIPPED_FILE)

        try:
            await bot.answer_callback_query(callback_query.id, text="Skipped.")
        except TelegramBadRequest as e:
            if "query is too old" in str(e):
                logger.warning("Callback query expired, ignoring.")
            else:
                raise

    await send_vacancy_to_user(user_id)
