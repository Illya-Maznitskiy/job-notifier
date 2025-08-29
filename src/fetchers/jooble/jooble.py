import asyncio
from typing import List

from src.db.db import AsyncSessionLocal
from src.fetchers.jooble.fetcher import fetch_jooble_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> List[dict]:
    """Fetch jobs from Jooble and save to DB."""
    logger.info("-" * 60)
    logger.info("Starting Jooble fetch and save operation")

    jobs: List[dict] = []
    try:
        jobs = fetch_jooble_jobs()  # sync call
        if not jobs:
            logger.info("No jobs fetched from jooble.")
        else:
            async with AsyncSessionLocal() as session:
                await save_jobs_to_db(jobs, session)
    except Exception as fetch_save_err:
        logger.error(f"Error during fetch/save: {fetch_save_err}")

    logger.info("Jooble job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
