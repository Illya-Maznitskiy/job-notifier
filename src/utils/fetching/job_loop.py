import asyncio
from datetime import datetime, timedelta

from logs.logger import logger
from src.utils.fetching.fetch_orchestrator import run_all_fetchers
from src.utils.resources_logging import log_resources


async def job_process_loop() -> None:
    """
    Periodically runs job fetching.
    Runs every 12 hours.
    """
    sleep_hours = 12
    sleep_seconds = sleep_hours * 60 * 60

    # Initial delay to let the bot settle before first fetch
    initial_sleep = 3 * 60
    logger.info(
        f"Waiting {initial_sleep // 60} minutes before first job fetch..."
    )
    await asyncio.sleep(initial_sleep)
    logger.info("Starting first job fetch now.")

    while True:
        log_resources()
        start_time = datetime.now()
        next_run_time = start_time + timedelta(seconds=sleep_seconds)

        try:
            logger.info("-" * 60)
            logger.info(f"Job processing started at {start_time}")
            logger.info(f"Next job processing scheduled at {next_run_time}")

            await run_all_fetchers()

        except Exception as e:
            logger.warning(f"Job process failed: {e}")

        finally:
            end_time = datetime.now()
            log_resources()
            logger.info(f"Job processing finished at {end_time}")
            logger.info(f"Next job processing will be at {next_run_time}")

        await asyncio.sleep(sleep_seconds)


if __name__ == "__main__":
    asyncio.run(job_process_loop())
