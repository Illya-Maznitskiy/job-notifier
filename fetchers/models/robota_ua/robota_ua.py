import asyncio

from fetchers.models.robota_ua.fetcher import fetch_robota_ua_jobs
from fetchers.utils.save_jobs import save_jobs_to_json
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs = await fetch_robota_ua_jobs()
    save_jobs_to_json(jobs, "robota_ua.json")

    logger.info("Fetch and save completed")

    return jobs


if __name__ == "__main__":
    asyncio.run(run_fetch_and_save_jobs())
