import asyncio
from datetime import datetime, timedelta

from logs.logger import logger
from src.utils.fetching.fetch_orchestrator import run_all_fetchers


async def job_process_loop() -> None:
    """
    Periodically runs job fetching.
    Runs every 12 hours.
    """
    sleep_hours = 12
    sleep_seconds = sleep_hours * 60 * 60

    while True:
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
            logger.info(f"Job processing finished at {end_time}")
            logger.info(f"Next job processing will be at {next_run_time}")

        await asyncio.sleep(sleep_seconds)


if __name__ == "__main__":
    asyncio.run(job_process_loop())
