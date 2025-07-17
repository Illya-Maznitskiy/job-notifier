from fetchers.justjoin.fetcher import fetch_jobs
from fetchers.save_jobs import save_jobs_to_json
from logs.logger import logger


async def run_fetch_and_save_jobs():
    """
    Fetch jobs asynchronously and save to JSON file.
    """
    jobs = await fetch_jobs()

    if not jobs:
        logger.info("no_jobs")
    else:
        save_jobs_to_json(jobs, "justjoin_jobs.json")

    return jobs
