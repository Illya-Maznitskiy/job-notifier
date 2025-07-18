import asyncio

from logs.logger import logger
from storage.combine_json import save_all_vacancies
from utils.fetch_orchestrator import run_all_fetchers
from utils.job_filter import filter_and_score_jobs_from_file


async def main():
    """
    Run job fetchers and save all vacancies asynchronously.
    """
    logger.info("-" * 60)
    logger.info("Starting job fetchers")

    # Fetch all jobs
    all_jobs = await run_all_fetchers()
    logger.info(f"Total jobs fetched: {len(all_jobs)}")

    # Save all fetched jobs to storage
    save_all_vacancies()
    logger.info("All jobs saved successfully")

    # Filter and score jobs
    filtered_jobs = filter_and_score_jobs_from_file()
    logger.info(
        f"Filtering done. {len(filtered_jobs)} jobs passed the threshold."
    )


if __name__ == "__main__":
    asyncio.run(main())
