from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.job import get_job_by_url, create_job
from logs.logger import logger


async def save_jobs_to_db(jobs, session: AsyncSession):
    """Save jobs to database if not already existing."""
    for job_data in jobs:
        existing_job = await get_job_by_url(session, job_data["url"])
        if not existing_job:
            await create_job(
                session,
                title=job_data.get("title"),
                company=job_data.get("company"),
                location=job_data.get("location"),
                salary=job_data.get("salary"),
                skills=job_data.get("skills"),
                score=job_data.get("score", 0),
                url=job_data.get("url"),
            )
        else:
            logger.info(
                f"Skipping {job_data.get('title')} because it already exists."
            )
