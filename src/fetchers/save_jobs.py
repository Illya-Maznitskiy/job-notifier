from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.job import get_job_by_url, create_job
from logs.logger import logger


MAX_LOCATION_LENGTH = 255
MAX_TITLE_LENGTH = 255


async def save_jobs_to_db(jobs, session: AsyncSession):
    """Save jobs to database if not already existing. Truncate fields that are too long."""
    for job_data in jobs:
        existing_job = await get_job_by_url(session, job_data["url"])
        if not existing_job:
            title = job_data.get("title")
            location = job_data.get("location")

            if title and len(title) > MAX_TITLE_LENGTH:
                title = title[:MAX_TITLE_LENGTH]

            if location and len(location) > MAX_LOCATION_LENGTH:
                location = location[:MAX_LOCATION_LENGTH]

            await create_job(
                session,
                title=title,
                company=job_data.get("company"),
                location=location,
                salary=job_data.get("salary"),
                skills=job_data.get("skills"),
                score=job_data.get("score", 0),
                url=job_data.get("url"),
            )
        else:
            logger.info(
                f"Skipping {job_data.get('title')} because it already exists."
            )
