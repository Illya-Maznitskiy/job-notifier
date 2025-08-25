import asyncio

from logs.logger import logger
from src.utils.email_sender import send_job_listings_email
from src.utils.fetch_orchestrator import run_all_fetchers


JOB_LOOP_INTERVAL = 12 * 3600


async def job_process_loop():
    """
    Periodically runs job fetching, saving, emailing.
    Runs every 12 hour.
    """
    # wait 12 hours before next fetch

    while True:
        logger.info("-" * 60)
        logger.info("Job processing started")

        await run_all_fetchers()
        send_job_listings_email()

        await asyncio.sleep(JOB_LOOP_INTERVAL)


if __name__ == "__main__":
    asyncio.run(job_process_loop())
