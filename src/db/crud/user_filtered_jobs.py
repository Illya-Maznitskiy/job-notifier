from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import UserFilteredJob


# Create
async def create_user_filtered_job(
    session: AsyncSession, user_id: int, job_id: int, score: int
):
    entry = UserFilteredJob(user_id=user_id, job_id=job_id, score=score)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


# Read all for a user
async def get_filtered_jobs_by_user(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(UserFilteredJob)
        .where(UserFilteredJob.user_id == user_id)
        .order_by(UserFilteredJob.score.desc())
    )
    return result.scalars().all()


# Read single
async def get_filtered_job(session: AsyncSession, user_id: int, job_id: int):
    result = await session.execute(
        select(UserFilteredJob).where(
            UserFilteredJob.user_id == user_id,
            UserFilteredJob.job_id == job_id,
        )
    )
    return result.scalar_one_or_none()


# Update score
async def update_filtered_job_score(
    session: AsyncSession, user_id: int, job_id: int, new_score: int
):
    await session.execute(
        update(UserFilteredJob)
        .where(
            UserFilteredJob.user_id == user_id,
            UserFilteredJob.job_id == job_id,
        )
        .values(score=new_score)
    )
    await session.commit()


# Delete
async def delete_filtered_job(
    session: AsyncSession, user_id: int, job_id: int
):
    await session.execute(
        delete(UserFilteredJob).where(
            UserFilteredJob.user_id == user_id,
            UserFilteredJob.job_id == job_id,
        )
    )
    await session.commit()
