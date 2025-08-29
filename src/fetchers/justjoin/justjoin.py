import asyncio
from typing import List, Dict, Any

from src.db.db import AsyncSessionLocal
from src.fetchers.justjoin.fetcher import fetch_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> List[Dict[str, Any]]:
    """Fetch jobs asynchronously and save to DB."""
    jobs: List[Dict[str, Any]] = []
    try:
        jobs = await fetch_jobs()
        if not jobs:
            logger.info("No jobs fetched from justjoin.")
        else:
            async with AsyncSessionLocal() as session:
                await save_jobs_to_db(jobs, session)
    except Exception as err:
        logger.error(f"Error fetching/saving jobs: {err}")

    logger.info("Justjoin job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as main_err:
        logger.error(f"Unhandled error: {main_err}")
