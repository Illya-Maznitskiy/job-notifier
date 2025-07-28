from fetchers.models.jooble.fetcher import fetch_jooble_jobs
from fetchers.utils.save_jobs import save_jobs_to_json
from logs.logger import logger


async def run_fetch_and_save_jobs():
    logger.info("-" * 60)
    logger.info("Starting Jooble fetch and save operation")

    jobs = fetch_jooble_jobs()  # sync call here
    save_jobs_to_json(jobs, "jooble_jobs.json")

    logger.info("Jooble fetch and save completed")
    return jobs


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_fetch_and_save_jobs())
