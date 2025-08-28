import asyncio

from src.config import PRACUJ_URL
from src.db.db import AsyncSessionLocal
from src.fetchers.pracuj.fetcher import fetch_pracuj_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    if not PRACUJ_URL:
        logger.error("Config variable NO_FLUFF_URL not found.")
        return None

    jobs = await fetch_pracuj_jobs(PRACUJ_URL)

    for i, job in enumerate(jobs, 1):
        logger.info(
            f"{i:>3}. {job['title']:<60} @ {job.get('company', 'unknown')}"
        )

    if not jobs:
        logger.info("No jobs fetched from pracuj.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("Pracuj job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
