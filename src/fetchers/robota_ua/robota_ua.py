import asyncio

from src.db.db import AsyncSessionLocal
from src.fetchers.robota_ua.fetcher import fetch_robota_ua_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> list[dict]:
    """Fetch and save Robota UA jobs."""
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs: list[dict] = []
    try:
        jobs = await fetch_robota_ua_jobs()
        if jobs:
            async with AsyncSessionLocal() as session:
                await save_jobs_to_db(jobs, session)
        else:
            logger.info("No jobs fetched from robota ua.")
    except Exception as fetch_err:
        logger.error(f"Failed during fetch/save: {fetch_err}")

    logger.info("Robota ua job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as err:
        logger.error(f"Top-level error: {err}")
