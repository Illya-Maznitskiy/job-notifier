import asyncio

from src.db.db import AsyncSessionLocal
from src.fetchers.robota_ua.fetcher import fetch_robota_ua_jobs
from src.fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs = await fetch_robota_ua_jobs()

    if not jobs:
        logger.info("No jobs fetched from robota ua.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("Robota ua job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
