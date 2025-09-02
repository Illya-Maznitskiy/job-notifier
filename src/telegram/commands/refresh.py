from aiogram import types
from sqlalchemy import select, delete

from src.db.db import AsyncSessionLocal
from src.db.models import Job, UserFilteredJob
from logs.logger import logger
from src.telegram.bot_config import dp
from aiogram.filters import Command

from src.telegram.job_utils import get_or_create_user
from src.utils.job_filter import filter_jobs_for_user
from src.db.crud.user_filtered_jobs import (
    create_user_filtered_jobs,
)


@dp.message(Command("refresh"))
async def refresh_jobs(message: types.Message) -> None:
    """Filter and save jobs for user browsing."""
    logger.info("-" * 60)
    logger.info(f"Refreshing jobs for user: {message.from_user.id}")

    try:
        async with AsyncSessionLocal() as session:
            await message.answer("⏳ Filtering jobs, please wait…")

            # Ensure user exists
            user = await get_or_create_user(
                session, message.from_user.id, message.from_user.username
            )

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

            # Filter jobs for the user (returns list of tuples: (job, score))
            logger.info("Starting job filtering")
            filtered_jobs = await filter_jobs_for_user(session, user.id, jobs)
            logger.info(f"Filtering done, found {len(filtered_jobs)} jobs")
            logger.info("Saving filtered vacancies to DB")

            # Save filtered jobs to DB using CRUD
            entries = [
                UserFilteredJob(user_id=user.id, job_id=job.id, score=score)
                for job, score in filtered_jobs
            ]
            await create_user_filtered_jobs(session, entries)

            logger.info(f"Found {len(filtered_jobs)} jobs for user {user.id}")

        await message.answer(
            f"✅ Found {len(filtered_jobs)} relevant jobs. Use /vacancy to get your jobs"
        )
    except Exception as e:
        logger.error(
            f"Error refreshing jobs for user {message.from_user.id}: {e}"
        )
        await message.answer("⚠️ Failed to refresh jobs. Try again later.")
