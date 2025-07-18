import asyncio
from pathlib import Path

from logs.logger import logger
from storage.combine_json import save_all_vacancies
from utils.fetch_orchestrator import run_all_fetchers


async def main():
    """
    Run job fetchers and save all vacancies asynchronously.
    """
    logger.info("-" * 60)
    logger.info("Starting job fetchers")

    all_jobs = await run_all_fetchers()
    logger.info(f"Total jobs fetched: {len(all_jobs)}")

    storage_dir = Path(__file__).resolve().parent / "storage"
    save_all_vacancies(storage_dir)

    logger.info("All jobs saved successfully")


if __name__ == "__main__":
    asyncio.run(main())
