import asyncio

from db.db import AsyncSessionLocal
from fetchers.djinni.fetcher import fetch_jobs
from fetchers.save_jobs import save_jobs_to_db
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs = await fetch_jobs()

    if not jobs:
        logger.info("No jobs fetched from djinni.")
    else:
        async with AsyncSessionLocal() as session:
            await save_jobs_to_db(jobs, session)

    logger.info("Djinni job fetch process completed.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
