from fetchers.djinni.fetcher import fetch_jobs
from fetchers.djinni.save import save_jobs_to_json
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting full fetch and save operation")

    jobs = await fetch_jobs()
    save_jobs_to_json(jobs)

    logger.info("Fetch and save completed")

    return jobs
