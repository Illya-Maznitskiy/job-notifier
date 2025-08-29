import asyncio

from src.config import NO_FLUFF_URL
from src.db.db import AsyncSessionLocal
from src.fetchers.nofluff.fetcher import fetch_nofluff_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> list | None:
    """Fetch and save nofluff jobs."""
    if not NO_FLUFF_URL:
        logger.error("Config variable NO_FLUFF_URL not found.")
        return None

    logger.info("-" * 60)
    logger.info(f"Fetching jobs from: {NO_FLUFF_URL}")

    try:
        jobs = await fetch_nofluff_jobs(NO_FLUFF_URL)

        if jobs:
            async with AsyncSessionLocal() as session:
                await save_jobs_to_db(jobs, session)
        else:
            logger.info("No jobs fetched from nofluff.")
    except Exception as fetch_err:
        logger.error(f"Error fetching or saving jobs: {fetch_err}")
        return None

    logger.info("Nofluff job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as main_err:
        logger.error(f"Fatal error: {main_err}")
