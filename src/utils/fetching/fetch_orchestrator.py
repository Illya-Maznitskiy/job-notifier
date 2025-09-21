import asyncio

from src.fetchers.justjoin.justjoin import (
    run_fetch_and_save_jobs as fetch_justjoin,
)
from src.fetchers.djinni.djinni import run_fetch_and_save_jobs as fetch_djinni
from src.fetchers.nofluff.nofluff import (
    run_fetch_and_save_jobs as fetch_nofluff,
)
from src.fetchers.pracuj.pracuj import run_fetch_and_save_jobs as fetch_pracuj
from src.fetchers.dou.dou import run_fetch_and_save_jobs as fetch_dou
from src.fetchers.bulldog.bulldog import (
    run_fetch_and_save_jobs as fetch_bulldog,
)
from src.fetchers.robota_ua.robota_ua import (
    run_fetch_and_save_jobs as fetch_robota_ua,
)
from src.fetchers.jooble.jooble import run_fetch_and_save_jobs as fetch_jooble
from logs.logger import logger
from src.utils.resources_logging import log_resources

FETCHERS = {
    "justjoin": fetch_justjoin,
    "djinni": fetch_djinni,
    "nofluff": fetch_nofluff,
    "pracuj": fetch_pracuj,
    "dou": fetch_dou,
    "bulldog": fetch_bulldog,
    "robota_ua": fetch_robota_ua,
    "jooble": fetch_jooble,
}


async def run_all_fetchers() -> list[dict]:
    """
    Runs all job fetchers and combines their results.
    """
    all_jobs = []

    for name, fetcher in FETCHERS.items():
        logger.info("-" * 60)
        log_resources()
        logger.info(f"Fetching jobs from {name}...")
        try:
            jobs = await fetcher()
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error fetching from {name}: {e}", exc_info=True)
        finally:
            log_resources()

    logger.info(f"Total jobs fetched: {len(all_jobs)}")

    return all_jobs


if __name__ == "__main__":
    asyncio.run(run_all_fetchers())
