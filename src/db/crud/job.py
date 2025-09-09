from datetime import datetime, timezone, timedelta

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from logs.logger import logger
from src.config import JOB_ARCHIVE_DAYS
from src.db.models.job import Job


async def get_job_by_url(session: AsyncSession, url: str) -> Job | None:
    """Fetch a Job by URL."""
    try:
        result = await session.execute(select(Job).where(Job.url == url))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Failed to fetch job by URL '{url}': {e}")
        return None


async def get_job_by_id(session: AsyncSession, job_id: int) -> Job | None:
    """Fetch a Job by ID."""
    try:
        result = await session.execute(select(Job).where(Job.id == job_id))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Failed to fetch job {job_id}: {e}")
        return None


async def create_job(
    session: AsyncSession,
    title: str,
    company: str,
    location: str | None,
    salary: str | None,
    skills: list[str] | None,
    score: int,
    url: str,
) -> Job | None:
    """Create and save a new Job."""
    try:
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
    except Exception as e:
        logger.error(f"Failed to create job '{title}': {e}")
        return None


async def create_multiple_jobs(session: AsyncSession, jobs_data: list[dict]):
    """Insert multiple jobs at once."""
    if not jobs_data:
        return

    try:
        stmt = insert(Job).values(jobs_data)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to insert multiple jobs: {e}")


async def update_jobs_last_seen_archived_at(
    session: AsyncSession, urls: list[str]
) -> None:
    """Update last_seen and extend archived_at for jobs found again."""
    if not urls:
        logger.info("No URLs provided for updating jobs.")
        return

    now = datetime.now(timezone.utc)
    new_archived_at = now + timedelta(days=JOB_ARCHIVE_DAYS)

    try:
        await session.execute(
            update(Job)
            .where(Job.url.in_(urls))
            .values(last_seen=now, archived_at=new_archived_at)
        )
        await session.commit()
        logger.info(
            f"Updated last_seen and extended archived_at for {len(urls)} jobs."
        )
    except Exception as e:
        logger.error(
            f"Failed to update last_seen or archived_at for jobs: {e}"
        )
