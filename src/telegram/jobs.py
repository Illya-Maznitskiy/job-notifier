import random

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.job import get_job_by_id
from src.db.crud.user_filtered_jobs import get_filtered_jobs_by_user
from src.db.crud.user_job import (
    get_user_job,
    create_user_job,
    update_user_job_status,
)
from src.db.db import AsyncSessionLocal
from src.db.models import Job
from .bot_config import (
    bot,
    dp,
    user_request_count,
    MEME_GIFS,
)
from logs.logger import logger
from src.telegram.job_utils import (
    clean_short_title,
    create_vacancy_message,
    get_or_create_user,
)


async def send_vacancy_to_user(
    user_id: str, session: AsyncSession, username: str | None = None
):
    """Send next unviewed vacancy to the user."""
    logger.info("-" * 60)
    logger.info(f"Sending vacancy to user: {user_id}")

    user = await get_or_create_user(session, int(user_id), username)

    user_filtered_jobs = await get_filtered_jobs_by_user(session, user.id)
    job_sent = False

    if not user_filtered_jobs:
        await bot.send_message(
            user_id,
            "You have no filters set ⏳ Use /add_keyword <keyword> <weight> first",
        )
        await bot.send_message(user_id, "💡 Example /add_keyword python 10")
        return

    for ufj in user_filtered_jobs:
        # check if user has already seen/applied/skipped this job
        user_job = await get_user_job(session, user.id, ufj.job_id)
        if user_job and user_job.status in ("sent", "applied", "skipped"):
            continue  # skip jobs already sent or acted upon

        job: Job | None = await session.get(Job, ufj.job_id)
        if not job:
            continue

        # mark as sent
        await create_user_job(session, user.id, job.id, status="sent")

        msg, keyboard = create_vacancy_message(job, score=ufj.score)
        await bot.send_message(
            user_id, msg, reply_markup=keyboard, parse_mode="Markdown"
        )
        job_sent = True
        break

    if not job_sent:
        logger.info(f"No new vacancies for user {user_id}")
        await bot.send_message(
            user_id, "🫠 Dried up. Jobs gone. I am but dust"
        )


@dp.callback_query(
    lambda c: c.data and c.data.startswith(("applied|", "skip|"))
)
async def process_callback(callback_query: types.CallbackQuery):
    """Handle user 'applied' or 'skip' button clicks."""
    logger.info("-" * 60)

    action, job_id = callback_query.data.split("|", 1)
    user_id = str(callback_query.from_user.id)
    logger.info(f"Callback from user {user_id}: {action}")

    # ✅ Open DB session here
    async with AsyncSessionLocal() as session:
        async with session.begin():  # transaction
            # Get the job
            job = await get_job_by_id(session, int(job_id))
            if not job:
                logger.warning(f"Job not found: {job_id}, {job}")
                await bot.answer_callback_query(
                    callback_query.id, text="Job not found."
                )
                return

            # Get or create the user
            user = await get_or_create_user(
                session, int(user_id), callback_query.from_user.username
            )

            # Get or create the user_job record
            user_job = await get_user_job(session, user.id, job.id)
            if not user_job:
                user_job = await create_user_job(
                    session, user.id, job.id, status="sent"
                )

            # Update status
            new_status = "applied" if action == "applied" else "skipped"
            await update_user_job_status(session, user_job, new_status)

        # Commit automatically happens when leaving `session.begin()`

    short_title = clean_short_title(job.title)
    reply_text = (
        f"Marked '{short_title}' as {new_status} 😎"
        if action == "applied"
        else "Skipped."
    )

    try:
        await bot.answer_callback_query(callback_query.id, text=reply_text)
    except TelegramBadRequest as e:
        if "query is too old" in str(e):
            logger.warning("Callback query expired, ignoring.")
        else:
            raise

    # Optionally, send a meme after every 3 requests
    if action == "applied":
        user_request_count[user_id] += 1
        if user_request_count[user_id] % 3 == 0:
            meme_url = random.choice(MEME_GIFS)
            await callback_query.message.answer_animation(meme_url)
            logger.info(f"Sent meme to user {user_id}")

    # ✅ Open a new session for sending the vacancy
    async with AsyncSessionLocal() as session2:
        await send_vacancy_to_user(user_id, session2)
