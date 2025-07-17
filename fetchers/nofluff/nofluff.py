import asyncio
import os
from dotenv import load_dotenv

from fetcher import fetch_nofluff_jobs
from fetchers.save_jobs import save_jobs_to_json
from logs.logger import logger


load_dotenv()
NO_FLUFF_URL = os.getenv("NO_FLUFF_URL")


async def run_fetch_and_save_jobs():
    if not NO_FLUFF_URL:
        logger.error("Environment variable NO_FLUFF_URL not found.")
        return

    logger.info("-" * 60)
    logger.info(f"Fetching jobs from: {NO_FLUFF_URL}")

    jobs = await fetch_nofluff_jobs(NO_FLUFF_URL)

    for i, job in enumerate(jobs, 1):
        logger.info(f"{i}. {job}")

    save_jobs_to_json(jobs, filename="nofluff_jobs.json")
    logger.info("Job titles saved successfully.")


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
