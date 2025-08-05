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
    make_job_key,
    create_vacancy_message,
)
from notifier.telegram.job_utils import find_job_by_hash


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

    user_applied = applied_jobs.get(user_id, [])
    user_skipped = skipped_jobs.get(user_id, [])
    applied_keys = {entry["job_key"] for entry in user_applied}
    skipped_keys = {entry["job_key"] for entry in user_skipped}

    for job in vacancies:
        job_key = make_job_key(job)

        if job_key not in applied_keys and job_key not in skipped_keys:
            msg, keyboard = create_vacancy_message(job)
            await bot.send_message(
                user_id, msg, reply_markup=keyboard, parse_mode="Markdown"
            )
            logger.info(f"Sent vacancy {job_key} to user {user_id}")
            return

    logger.info(f"No new vacancies for user {user_id}")
    await bot.send_message(user_id, "🫠 Dried up. Jobs gone. I am but dust")


@dp.callback_query(
    lambda c: c.data and c.data.startswith(("applied|", "skip|"))
)
async def process_callback(callback_query: types.CallbackQuery):
    """Handle user 'applied' or 'skip' button clicks."""
    logger.info("-" * 60)

    action, job_hash = callback_query.data.split("|", 1)
    user_id = str(callback_query.from_user.id)
    logger.info(f"Callback from user {user_id}: {action}")

    job = find_job_by_hash(job_hash, FILTERED_FILE)
    if not job:
        logger.warning(f"Job not found for hash: {job_hash}")
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
    job_key = make_job_key(job)
    now_str = datetime.utcnow().isoformat()

    job_data = {
        "job_key": job_key,
        "url": job_url,
        "datetime": now_str,
    }
    logger.info(f"User {user_id} marked job '{title}' as '{action}'")

    if action == "applied":
        applied_jobs.setdefault(user_id, []).append(job_data)
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
        skipped_jobs.setdefault(user_id, []).append(job_data)
        save_skipped(skipped_jobs, SKIPPED_FILE)
        try:
            await bot.answer_callback_query(callback_query.id, text="Skipped.")
        except TelegramBadRequest as e:
            if "query is too old" in str(e):
                logger.warning("Callback query expired, ignoring.")
            else:
                raise

    await send_vacancy_to_user(user_id)
