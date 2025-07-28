import asyncio

from fetchers.models.dou.fetcher import fetch_jobs
from fetchers.utils.save_jobs import save_jobs_to_json
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
        save_jobs_to_json(jobs, "dou_jobs.json")

    logger.info("DOU job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
