import asyncio
from typing import List, Dict, Any

from src.db.db import AsyncSessionLocal
from src.fetchers.dou.fetcher import fetch_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> List[Dict[str, Any]]:
    """Fetch DOU jobs and save them asynchronously."""
    logger.info("-" * 60)
    logger.info("Starting DOU job fetch & save process...")

    try:
        jobs = await fetch_jobs()
    except Exception as fetch_err:
        logger.exception(f"Error fetching jobs: {fetch_err}")
        return []

    if not jobs:
        logger.info("No jobs fetched from DOU.")
        return []

    try:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)
    except Exception as save_err:
        logger.exception(f"Error saving jobs: {save_err}")
        return []

    logger.info("DOU job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as main_err:
        logger.exception(f"Unhandled error in main: {main_err}")
