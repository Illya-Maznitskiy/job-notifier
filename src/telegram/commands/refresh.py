from datetime import date

from aiogram import types
from sqlalchemy import select, delete

from src.db.crud.user_keyword import get_user_all_keywords
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
            user_id = user.id

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

            if not await get_user_all_keywords(session, user_id):
                await message.answer(
                    "You have no keywords set 😬\nUse /add to add some 😇"
                )
                logger.info(
                    f"No keywords for user {telegram_id}, "
                    f"skipping job filtering"
                )
                return

            user.refresh_count += 1

            await message.answer("⏳ Filtering jobs, please wait…")

            # Get user's region
            result = await session.execute(
                select(UserRegion.region).where(UserRegion.user_id == user_id)
            )
            region = result.scalar()  # None if not set

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
            logger.info(f"Starting job filtering for user {telegram_id}")
            filtered_jobs = await filter_jobs_for_user(
                session, user_id, telegram_id, jobs
            )
            if not filtered_jobs:
                logger.info(f"Sending no jobs message to user {telegram_id}")
                keywords = await get_user_all_keywords(session, user_id)
                reply = "No jobs found for your keywords 🥲"
                for kw in keywords:
                    reply += f"\n• {kw.keyword} ({kw.weight})"
                await message.answer(reply)

                await message.answer(
                    "Try other keywords /add, "
                    "or report issues via /feedback 🐞"
                )

                logger.info(
                    f"No jobs found for user {telegram_id} with keywords "
                    f"{[kw.keyword for kw in keywords]}"
                )
                return

            logger.info(f"Filtering done, found {len(filtered_jobs)} jobs")

            # Delete old filtered jobs for this user
            logger.info(f"Deleting old filtered jobs for user {telegram_id}")
            await session.execute(
                delete(UserFilteredJob).where(
                    UserFilteredJob.user_id == user_id
                )
            )
            await session.commit()

            # Save new filtered jobs to DB using CRUD
            logger.info("Saving new filtered vacancies to DB")
            entries = [
                UserFilteredJob(user_id=user_id, job_id=job.id, score=score)
                for job, score in filtered_jobs
            ]
            await create_user_filtered_jobs(session, entries)

            await message.answer(
                f"✅ Found {len(filtered_jobs)} relevant jobs. Use "
                f"/vacancy to get your jobs"
            )
            logger.info(
                f"Found {len(filtered_jobs)} jobs for user {telegram_id}"
            )

    except Exception as e:
        logger.error(f"Error refreshing jobs for user {telegram_id}: {e}")
        await message.answer("⚠️ Failed refreshing jobs. Try again later 🫠")
