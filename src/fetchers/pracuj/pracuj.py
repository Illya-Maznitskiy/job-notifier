import asyncio

from tqdm.asyncio import tqdm_asyncio

from src.config import PRACUJ_URL
from src.db.db import AsyncSessionLocal
from src.fetchers.pracuj.fetcher import fetch_pracuj_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs() -> list[dict] | None:
    """Fetch jobs and save to DB."""
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    if not PRACUJ_URL:
        logger.error("Config variable PRACUJ_URL not found.")
        return None

    try:
        jobs = await fetch_pracuj_jobs(PRACUJ_URL)
    except Exception as fetch_err:
        logger.error(f"Failed fetching jobs: {fetch_err}")
        return []

    for i, job in enumerate(
        tqdm_asyncio(jobs, desc="Fetching jobs", mininterval=10.0), 1
    ):
        logger.debug(
            f"{i:>3}. {job['title']:<60} @ {job.get('company', 'unknown')}"
        )

    if not jobs:
        logger.info("No jobs fetched from pracuj.")
        return []

    try:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)
    except Exception as db_err:
        logger.error(f"Failed saving jobs to DB: {db_err}")
        return jobs

    logger.info("Pracuj job fetch process completed.")
    return jobs


if __name__ == "__main__":
    try:
        asyncio.run(run_fetch_and_save_jobs())
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
