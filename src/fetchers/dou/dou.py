import asyncio

from src.db.db import AsyncSessionLocal
from src.fetchers.dou.fetcher import fetch_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    """
    Fetch DOU jobs asynchronously and save to JSON file.
    """
    logger.info("-" * 60)
    logger.info("Starting DOU job fetch & save process...")

    jobs = await fetch_jobs()

    if not jobs:
        logger.info("No jobs fetched from DOU.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("DOU job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
