from fetchers.justjoin.justjoin import (
    run_fetch_and_save_jobs as fetch_justjoin,
)
from fetchers.djinni.djinni import run_fetch_and_save_jobs as fetch_djinni
from fetchers.nofluff.nofluff import run_fetch_and_save_jobs as fetch_nofluff
from fetchers.pracuj.pracuj import run_fetch_and_save_jobs as fetch_pracuj
from fetchers.dou.dou import run_fetch_and_save_jobs as fetch_dou
from fetchers.bulldog.bulldog import run_fetch_and_save_jobs as fetch_bulldog
from logs.logger import logger


FETCHERS = {
    "justjoin": fetch_justjoin,
    "djinni": fetch_djinni,
    "nofluff": fetch_nofluff,
    "pracuj": fetch_pracuj,
    "dou": fetch_dou,
    "bulldog": fetch_bulldog,
}


async def run_all_fetchers() -> list[dict]:
    """
    Runs all job fetchers and combines their results.
    """
    all_jobs = []

    for name, fetcher in FETCHERS.items():
        logger.info(f"Fetching jobs from {name}...")
        try:
            jobs = await fetcher()
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error fetching from {name}: {e}", exc_info=True)

    logger.info(f"Total jobs fetched: {len(all_jobs)}")

    return all_jobs
