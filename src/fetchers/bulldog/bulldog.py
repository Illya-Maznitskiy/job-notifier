import asyncio
from typing import List

from src.db.db import AsyncSessionLocal
from src.fetchers.bulldog.fetcher import fetch_bulldog_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> List[dict]:
    """
    Fetch jobs from Bulldog API and save them to the database.
    """
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    try:
        # Fetch jobs from the external Bulldog API
        jobs = await fetch_bulldog_jobs()
    except Exception as fetch_err:
        logger.exception("Error fetching jobs: %s", fetch_err)
        return []

    if not jobs:
        logger.info("No jobs fetched from bulldog.")
    else:
        try:
            # Save fetched jobs to the database asynchronously
            async with AsyncSessionLocal() as session:
                await save_jobs_to_db(jobs, session)
        except Exception as save_err:
            logger.exception("Error saving jobs: %s", save_err)
            return []

    logger.info("Bulldog job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        # Run the async job fetch/save process
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as main_err:
        logger.exception("Unhandled error in main: %s", main_err)
