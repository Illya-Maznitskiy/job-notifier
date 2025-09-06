from typing import Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from logs.logger import logger
from src.db.models import Job
from src.db.models.user_filtered_job import UserFilteredJob


async def create_user_filtered_jobs(
    session: AsyncSession, entries: list[UserFilteredJob]
) -> None:
    """Insert multiple UserFilteredJob entries."""
    try:
        session.add_all(entries)
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to insert user filtered jobs: {e}")


async def get_filtered_jobs_by_user(
    session: AsyncSession, user_id: int
) -> Sequence[UserFilteredJob]:
    """Fetch filtered jobs for a user ordered by score and newest jobs first."""
    try:
        result = await session.execute(
            select(UserFilteredJob)
            .where(UserFilteredJob.user_id == user_id)
            .join(UserFilteredJob.job)
            .order_by(UserFilteredJob.score.desc(), Job.last_seen.desc())
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Failed to fetch filtered jobs for user {user_id}: {e}")
        return []


async def get_filtered_job(
    session: AsyncSession, user_id: int, job_id: int
) -> UserFilteredJob | None:
    """Fetch a specific filtered job for a user."""
    try:
        result = await session.execute(
            select(UserFilteredJob).where(
                UserFilteredJob.user_id == user_id,
                UserFilteredJob.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(
            f"Failed to fetch filtered job {job_id} for user {user_id}: {e}"
        )
        return None


async def update_filtered_job_score(
    session: AsyncSession, user_id: int, job_id: int, new_score: int
) -> None:
    """Update score of a user's filtered job."""
    try:
        await session.execute(
            update(UserFilteredJob)
            .where(
                UserFilteredJob.user_id == user_id,
                UserFilteredJob.job_id == job_id,
            )
            .values(score=new_score)
        )
        await session.commit()
    except Exception as e:
        logger.error(
            f"Failed to update score for job {job_id} of user {user_id}: {e}"
        )


async def delete_filtered_job(
    session: AsyncSession, user_id: int, job_id: int
) -> None:
    """Delete a specific filtered job for a user."""
    try:
        await session.execute(
            delete(UserFilteredJob).where(
                UserFilteredJob.user_id == user_id,
                UserFilteredJob.job_id == job_id,
            )
        )
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to delete job {job_id} for user {user_id}: {e}")
