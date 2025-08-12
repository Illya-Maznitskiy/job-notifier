from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Job, UserJob
from datetime import datetime


# --- User CRUD ---


async def get_user_by_user_id(
    session: AsyncSession, user_id: int
) -> User | None:
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()


async def create_user(
    session: AsyncSession, user_id: int, username: str | None
) -> User:
    user = User(user_id=user_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# --- Job CRUD ---


async def get_job_by_url(session: AsyncSession, url: str) -> Job | None:
    result = await session.execute(select(Job).where(Job.url == url))
    return result.scalars().first()


async def create_job(
    session: AsyncSession,
    title: str,
    company: str,
    location: str | None,
    salary: str | None,
    skills: list[str] | None,
    score: int,
    url: str,
) -> Job:
    job = Job(
        title=title,
        company=company,
        location=location,
        salary=salary,
        skills=skills,
        score=score,
        url=url,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


# --- UserJob CRUD ---


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
    await session.commit()
    await session.refresh(user_job)
    return user_job


async def update_user_job_status(
    session: AsyncSession, user_job: UserJob, new_status: str
) -> UserJob:
    user_job.status = new_status
    await session.commit()
    await session.refresh(user_job)
    return user_job
