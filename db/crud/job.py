from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Job


async def get_job_by_url(session: AsyncSession, url: str) -> Job | None:
    result = await session.execute(select(Job).where(Job.url == url))
    return result.scalars().first()


async def get_job_by_id(session: AsyncSession, job_id: int) -> Job | None:
    result = await session.execute(select(Job).where(Job.id == job_id))
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
