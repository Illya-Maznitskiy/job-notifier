import asyncio

from logs.logger import logger
from notifier.email_sender import send_job_listings_email
from notifier.telegram.telegram_bot import dp, bot
from utils.fetch_orchestrator import run_all_fetchers
from utils.jobs_saving_processes import save_backup_and_filter_jobs
from utils.run_telegram_bot import run_telegram_bot


async def main():
    """
    Run job fetchers, save and filter vacancies,
    send email, and run telegram bot.
    """
    logger.info("-" * 60)
    logger.info("Job processing started")

    await run_all_fetchers()
    save_backup_and_filter_jobs()
    send_job_listings_email()
    await run_telegram_bot(dp, bot)


if __name__ == "__main__":
    asyncio.run(main())
