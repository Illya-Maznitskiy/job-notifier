import asyncio
import logging
from pathlib import Path

from logs.logger import logger
from fetchers.justjoin import fetch_jobs as justjoin_fetcher
from storage.save_json import save_all_vacancies


async def main():
    logger.info("-" * 60)
    logger.info("Starting job fetchers")

    all_jobs = []

    try:
        justjoin_jobs = await justjoin_fetcher()
        all_jobs.extend(justjoin_jobs)

        logger.info(f"Total jobs fetched: {len(all_jobs)}")

        storage_dir = Path(__file__).resolve().parent / "storage"
        save_all_vacancies(storage_dir)

        logger.info("All jobs saved successfully")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
