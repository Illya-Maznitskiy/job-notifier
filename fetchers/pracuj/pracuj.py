import asyncio
import os
from dotenv import load_dotenv

from fetchers.pracuj.fetcher import fetch_pracuj_jobs
from fetchers.save_jobs import save_jobs_to_json
from logs.logger import logger


load_dotenv()
PRACUJ_URL = os.getenv("PRACUJ_URL")


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    if not PRACUJ_URL:
        logger.error("Environment variable NO_FLUFF_URL not found.")
        return None

    jobs = await fetch_pracuj_jobs(PRACUJ_URL)

    for i, job in enumerate(jobs, 1):
        logger.info(f"{i}. {job["title"]} - {job["company"]}")

    save_jobs_to_json(jobs, filename="pracuj_jobs.json")
    logger.info("Job titles saved successfully.")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
