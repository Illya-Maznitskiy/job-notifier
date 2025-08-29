from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models import Job
from src.db.crud.job import create_multiple_jobs
from logs.logger import logger


MAX_LOCATION_LENGTH = 255
MAX_TITLE_LENGTH = 255


async def save_jobs_to_db(jobs: List[dict], session: AsyncSession):
    """Efficiently save jobs to the database if not already existing."""
    if not jobs:
        return

    # Fetch all existing URLs in one query
    urls = [job["url"] for job in jobs if "url" in job]
    result = await session.execute(select(Job.url).where(Job.url.in_(urls)))
    existing_urls = set(row[0] for row in result.all())

    # Filter out jobs that already exist
    new_jobs = []
    for job_data in jobs:
        url = job_data.get("url")
        if not url or url in existing_urls:
            logger.info(
                f"Skipping {job_data.get('title')} because it already exists."
            )
            continue

        title = job_data.get("title")
        location = job_data.get("location")

        if title and len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH]
        if location and len(location) > MAX_LOCATION_LENGTH:
            location = location[:MAX_LOCATION_LENGTH]

        new_jobs.append(
            {
                "title": title,
                "company": job_data.get("company"),
                "location": location,
                "salary": job_data.get("salary"),
                "skills": job_data.get("skills"),
                "score": job_data.get("score", 0),
                "url": url,
            }
        )

    if new_jobs:
        await create_multiple_jobs(session, new_jobs)
        logger.info(
            f"Successfully added {len(new_jobs)} new jobs to the database."
        )
    else:
        logger.info("No new jobs to add to the database.")
