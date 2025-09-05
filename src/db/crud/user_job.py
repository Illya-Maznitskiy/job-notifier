from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from logs.logger import logger
from src.db.models.user_job import UserJob


async def get_user_job(
    session: AsyncSession, user_id: int, job_id: int
) -> UserJob | None:
    """Fetch a specific UserJob for a user."""
    try:
        result = await session.execute(
            select(UserJob).where(
                UserJob.user_id == user_id, UserJob.job_id == job_id
            )
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(
            f"Failed to fetch UserJob {job_id} for user {user_id}: {e}"
        )
        return None


async def create_user_job(
    session: AsyncSession,
    user_id: int,
    job_id: int,
    status: str = "sent",
    datetime_sent: datetime | None = None,
) -> UserJob | None:
    """Create a new UserJob."""
    try:
        if datetime_sent is None:
            datetime_sent = datetime.now(timezone.utc)

        user_job = UserJob(
            user_id=user_id,
            job_id=job_id,
            status=status,
            datetime_sent=datetime_sent,
        )
        session.add(user_job)
        await session.flush()  # push to DB but do NOT commit
        await session.refresh(user_job)
        return user_job
    except Exception as e:
        logger.error(
            f"Failed to create UserJob {job_id} for user {user_id}: {e}"
        )
        return None


async def update_user_job_status(
    session: AsyncSession, user_job: UserJob, new_status: str
) -> UserJob | None:
    """Update status of a UserJob."""
    try:
        user_job.status = new_status
        await session.flush()  # just push changes
        await session.refresh(user_job)
        return user_job
    except Exception as e:
        logger.error(
            f"Failed to update status for UserJob {user_job.job_id}: {e}"
        )
        return None
