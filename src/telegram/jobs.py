import random
from datetime import date

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
from src.db.models.job import Job
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


MAX_VACANCIES_PER_DAY = 7


async def send_vacancy_to_user(
    user_id: str, session: AsyncSession, username: str | None = None
) -> None:
    """Send next unviewed vacancy to the user."""
    logger.info("-" * 60)
    logger.info(f"Sending vacancy to user: {user_id}")

    try:
        user = await get_or_create_user(session, int(user_id), username)

        if user.last_reset_date < date.today():
            user.refresh_count = 0
            user.vacancies_count = 0
            user.last_reset_date = date.today()
            await session.commit()
            logger.info(f"Reset daily counters for user {user.id}")

        if user.vacancies_count >= MAX_VACANCIES_PER_DAY:
            await bot.send_message(
                user_id, f"⚡ {MAX_VACANCIES_PER_DAY} jobs done today!"
            )
            await bot.send_message(
                user_id, "Support the bot for future updates 💎"
            )
            logger.info(f"User {user.id} reached daily limit")
            return

        user_filtered_jobs = await get_filtered_jobs_by_user(session, user.id)
        job_sent = False

        if not user_filtered_jobs:
            await bot.send_message(
                user_id,
                "You have no filters set ⏳ Use /add first",
            )
            return

        # check if user has already seen/applied/skipped this job
        for ufj in user_filtered_jobs:
            user_job = await get_user_job(session, user.id, ufj.job_id)
            if user_job and user_job.status in ("sent", "applied", "skipped"):
                continue

            job: Job | None = await session.get(Job, ufj.job_id)
            if not job:
                continue

            await create_user_job(session, user.id, job.id, status="sent")

            user.vacancies_count += 1
            await session.commit()
            logger.info(
                f"Sent job to user {user.id},"
                f" updated count {user.vacancies_count}"
            )

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

    except Exception as err:
        logger.exception(f"Failed sending vacancy to user {user_id}: {err}")


@dp.callback_query(
    lambda c: c.data and c.data.startswith(("applied|", "skip|"))
)
async def process_callback(callback_query: types.CallbackQuery) -> None:
    """Handle user 'applied' or 'skip' button clicks."""
    logger.info("-" * 60)

    action, job_id = callback_query.data.split("|", 1)
    user_id = str(callback_query.from_user.id)
    logger.info(f"Callback from user {user_id}: {action}")

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():  # transaction
                # Get the job
                job = await get_job_by_id(session, int(job_id))
                if not job:
                    logger.warning(f"Job not found: {job_id}")
                    await bot.answer_callback_query(
                        callback_query.id,
                        text="Job not found, system issue 🤷‍♂️",
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

        if action == "applied":
            user_request_count[user_id] = (
                user_request_count.get(user_id, 0) + 1
            )
            if user_request_count[user_id] % 3 == 0:
                meme_url = random.choice(MEME_GIFS)
                await callback_query.message.answer_animation(meme_url)
                logger.info(f"Sent meme to user {user_id}")

        # Send next vacancy safely
        try:
            async with AsyncSessionLocal() as session2:
                await send_vacancy_to_user(user_id, session2)
        except Exception as err:
            logger.exception(
                f"Failed sending next vacancy to user {user_id}: {err}"
            )

    except Exception as err:
        logger.exception(
            f"Error processing callback for user {user_id}: {err}"
        )
