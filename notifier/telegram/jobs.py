import json

from aiogram import types

from .bot_config import (
    bot,
    dp,
    FILTERED_FILE,
    applied_jobs,
    skipped_jobs,
    SKIPPED_FILE,
    APPLIED_FILE,
)
from logs.logger import logger
from notifier.telegram.job_utils import (
    save_applied,
    save_skipped,
    get_keyboard,
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

    for job in vacancies:
        if (
            job["title"] not in user_applied
            and job["title"] not in user_skipped
        ):
            logger.info(f"Found new job for user {user_id}: {job['title']}")

            keyboard = get_keyboard(job["title"])

            score = job.get("score", "No score")
            url = job.get("url", "")
            url_text = f"[Link]({url})" if url else "No URL provided"

            msg = (
                f"**{job.get('title', 'No Title')}**\n"
                f"*Company:* {job.get('company', 'Unknown')}\n"
                f"*Score:* {score}\n"
                f"*URL:* {url_text}\n\n"
                f"{job.get('description', '')[:500]}..."
            )

            await bot.send_message(
                user_id, msg, reply_markup=keyboard, parse_mode="Markdown"
            )
            return

    logger.info(f"No new vacancies for user {user_id}")
    await bot.send_message(
        user_id, "No new vacancies to show. Check back later!"
    )


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
        await bot.answer_callback_query(
            callback_query.id, text="Job not found."
        )
        return

    title = job["title"]
    logger.info(f"User {user_id} marked job '{title}' as '{action}'")

    if action == "applied":
        applied_jobs.setdefault(user_id, []).append(title)
        save_applied(applied_jobs, APPLIED_FILE)
        await bot.answer_callback_query(
            callback_query.id, text="Marked as applied!"
        )
        short_title = title[:10] + ("…" if len(title) > 10 else "")
        await bot.send_message(
            user_id, f"Great! Marked '{short_title}' as applied. 🎉"
        )

    elif action == "skip":
        skipped_jobs.setdefault(user_id, []).append(title)
        save_skipped(skipped_jobs, SKIPPED_FILE)
        await bot.answer_callback_query(callback_query.id, text="Skipped.")

    await send_vacancy_to_user(user_id)
