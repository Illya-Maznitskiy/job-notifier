import asyncio
from pathlib import Path

from logs.logger import logger
from fetchers.justjoin.justjoin import (
    run_fetch_and_save_jobs as justjoin_fetch_and_save_jobs,
)
from fetchers.djinni.djinni import (
    run_fetch_and_save_jobs as djinni_fetch_and_save_jobs,
)
from fetchers.nofluff.nofluff import (
    run_fetch_and_save_jobs as nofluff_fetch_and_save_jobs,
)
from fetchers.pracuj.pracuj import (
    run_fetch_and_save_jobs as pracuj_fetch_and_save_jobs,
)
from storage.combine_json import save_all_vacancies


async def main():
    """
    Run job fetchers and save all vacancies asynchronously.
    """
    logger.info("-" * 60)
    logger.info("Starting job fetchers")

    all_jobs = []

    try:
        justjoin_jobs = await justjoin_fetch_and_save_jobs()
        djinni_jobs = await djinni_fetch_and_save_jobs()
        nofluff_jobs = await nofluff_fetch_and_save_jobs()
        pracuj_jobs = await pracuj_fetch_and_save_jobs()

        all_jobs.extend(justjoin_jobs)
        all_jobs.extend(djinni_jobs)
        all_jobs.extend(nofluff_jobs)
        all_jobs.extend(pracuj_jobs)

        logger.info(f"Total jobs fetched: {len(all_jobs)}")

        storage_dir = Path(__file__).resolve().parent / "storage"
        save_all_vacancies(storage_dir)

        logger.info("All jobs saved successfully")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
