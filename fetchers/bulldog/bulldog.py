import asyncio

from fetchers.bulldog.fetcher import fetch_bulldog_jobs
from fetchers.save_jobs import save_jobs_to_json
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs = await fetch_bulldog_jobs()
    save_jobs_to_json(jobs, "bulldog_jobs.json")

    logger.info("Fetch and save completed")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
