from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserJob


async def get_user_job(
    session: AsyncSession, user_id: int, job_id: int
) -> UserJob | None:
    result = await session.execute(
        select(UserJob).where(
            UserJob.user_id == user_id, UserJob.job_id == job_id
        )
    )
    return result.scalars().first()


async def create_user_job(
    session: AsyncSession,
    user_id: int,
    job_id: int,
    status: str = "sent",
    datetime_sent: datetime | None = None,
) -> UserJob:
    if datetime_sent is None:
        datetime_sent = datetime.utcnow()

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


async def update_user_job_status(
    session: AsyncSession, user_job: UserJob, new_status: str
) -> UserJob:
    user_job.status = new_status
    await session.flush()  # just push changes
    await session.refresh(user_job)
    return user_job
