from datetime import date

from aiogram import types
from sqlalchemy import select, delete

from src.db.db import AsyncSessionLocal
from src.db.models.job import Job
from src.db.models.user_filtered_job import UserFilteredJob
from logs.logger import logger
from src.db.models.user_region import UserRegion
from src.telegram.bot_config import dp
from aiogram.filters import Command

from src.telegram.job_utils import get_or_create_user
from src.utils.telegram.job_filter import filter_jobs_for_user
from src.db.crud.user_filtered_jobs import (
    create_user_filtered_jobs,
)


MAX_REFRESH_PER_DAY = 3


REGION_MAP = {
    "robota_ua": "Ukraine",
    "djinni": "Ukraine",
    "dou": "Ukraine",
    "justjoin": "Poland",
    "nofluff": "Poland",
    "pracuj": "Poland",
    "bulldog": "Poland",
    "jooble": "All",
}


@dp.message(Command("refresh"))
async def refresh_jobs(message: types.Message) -> None:
    """Filter and save jobs for user browsing."""
    telegram_id = message.from_user.id

    logger.info("-" * 60)
    logger.info(f"Refreshing jobs for user: {telegram_id}")

    try:
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(
                session, telegram_id, message.from_user.username
            )
            logger.info(
                f"User {telegram_id} refresh count: "
                f"{user.refresh_count}/{MAX_REFRESH_PER_DAY}"
            )

            today = date.today()
            if user.last_reset_date != today:
                user.refresh_count = 0
                user.vacancies_count = 0
                user.last_reset_date = today
                logger.info(
                    f"User {telegram_id} daily counters reset for {today}"
                )

            if user.refresh_count >= MAX_REFRESH_PER_DAY:
                await message.answer(
                    f"Yo 😬 You've reached your daily refresh limit "
                    f"({MAX_REFRESH_PER_DAY})"
                )
                await message.answer("Support the bot for future upgrades ⚡")
                return

            user.refresh_count += 1
            await session.commit()

            await message.answer("⏳ Filtering jobs, please wait…")

            # Get user's region
            result = await session.execute(
                select(UserRegion.region).where(UserRegion.user_id == user.id)
            )
            region = result.scalar()  # None if not set

            # Delete old filtered jobs for this user
            await session.execute(
                delete(UserFilteredJob).where(
                    UserFilteredJob.user_id == user.id
                )
            )
            await session.commit()

            # Fetch all jobs
            all_jobs = await session.execute(select(Job))
            jobs = list(all_jobs.scalars())

            # URL-based region filtering
            if region and region != "all":
                allowed_keys = [
                    key for key, reg in REGION_MAP.items() if reg == region
                ]
                jobs = [
                    job
                    for job in jobs
                    if any(key in job.url for key in allowed_keys)
                ]

            # Filter jobs for the user (returns list of tuples: (job, score))
            logger.info("Starting job filtering")
            filtered_jobs = await filter_jobs_for_user(
                session, user.id, telegram_id, jobs
            )
            logger.info(f"Filtering done, found {len(filtered_jobs)} jobs")
            logger.info("Saving filtered vacancies to DB")

            # Save filtered jobs to DB using CRUD
            entries = [
                UserFilteredJob(user_id=user.id, job_id=job.id, score=score)
                for job, score in filtered_jobs
            ]
            await create_user_filtered_jobs(session, entries)

            if filtered_jobs:
                await message.answer(
                    f"✅ Found {len(filtered_jobs)} relevant jobs. Use "
                    f"/vacancy to get your jobs"
                )
            else:
                await message.answer(
                    "No jobs found for your keywords 🥲\n"
                    "Try more keywords, or report issues via /feedback!"
                )
                logger.info(
                    f"No jobs found for user {telegram_id} with keywords "
                    f"{[kw.keyword for kw in user.keywords]}"
                )

            logger.info(
                f"Found {len(filtered_jobs)} jobs for user {telegram_id}"
            )

    except Exception as e:
        logger.error(f"Error refreshing jobs for user {telegram_id}: {e}")
        await message.answer("⚠️ Failed refreshing jobs. Try again later 🫠")
