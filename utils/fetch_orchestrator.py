# It's an old method. I don't like it
# from fetchers.models.justjoin.justjoin import (
#     run_fetch_and_save_jobs as fetch_justjoin,
# )
# from fetchers.models.djinni.djinni import run_fetch_and_save_jobs as fetch_djinni
# from fetchers.models.nofluff.nofluff import run_fetch_and_save_jobs as fetch_nofluff
# from fetchers.models.pracuj.pracuj import run_fetch_and_save_jobs as fetch_pracuj
# from fetchers.models.dou import run_fetch_and_save_jobs as fetch_dou
# from fetchers.models.bulldog import run_fetch_and_save_jobs as fetch_bulldog
# from fetchers.models.robota_ua import (
#     run_fetch_and_save_jobs as fetch_robota_ua,
# )

# It is a better way because you don't have to add every time a new Fetcher
from fetchers import registered_fetchers, FetchJob

from logs.logger import logger



async def run_all_fetchers() -> list[FetchJob]:
    """
    Runs all job fetchers and combines their results.
    """
    done_jobs: list[FetchJob] = []

    for fetcher in registered_fetchers:
        logger.info(f"Fetching jobs from {fetcher.service_name}...")
        try:
            jobs = await fetcher.execute(save_jobs=True)
            done_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error fetching from {fetcher.service_name}: {e}", exc_info=True)

    logger.info(f"Total jobs fetched: {len(done_jobs)}")

    return done_jobs
