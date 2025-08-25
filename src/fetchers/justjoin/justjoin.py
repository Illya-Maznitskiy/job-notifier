import asyncio

from src.db.db import AsyncSessionLocal
from src.fetchers.justjoin.fetcher import fetch_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    """
    Fetch jobs asynchronously and save to JSON file.
    """
    jobs = await fetch_jobs()

    if not jobs:
        logger.info("No jobs fetched from justjoin.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("Justjoin job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
