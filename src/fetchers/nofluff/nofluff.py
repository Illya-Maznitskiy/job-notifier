import asyncio

from src.config import NO_FLUFF_URL
from src.db.db import AsyncSessionLocal
from src.fetchers.nofluff.fetcher import fetch_nofluff_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    if not NO_FLUFF_URL:
        logger.error("Config variable NO_FLUFF_URL not found.")
        return None

    logger.info("-" * 60)
    logger.info(f"Fetching jobs from: {NO_FLUFF_URL}")

    jobs = await fetch_nofluff_jobs(NO_FLUFF_URL)

    if not jobs:
        logger.info("No jobs fetched from nofluff.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("Nofluff job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
