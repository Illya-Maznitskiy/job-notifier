import asyncio

from logs.logger import logger
from notifier.email_sender import send_job_listings_email
from notifier.telegram_bot import dp, bot
from storage.combine_json import save_all_vacancies
from utils.fetch_orchestrator import run_all_fetchers
from utils.job_filter import filter_and_score_jobs_from_file


async def main():
    """
    Run job fetchers and save all vacancies asynchronously.
    """
    logger.info("-" * 60)
    logger.info("Starting job fetchers")

    # Fetch all jobs
    all_jobs = await run_all_fetchers()
    logger.info(f"Total jobs fetched: {len(all_jobs)}")

    # Save all fetched jobs to storage
    save_all_vacancies()
    logger.info("All jobs saved successfully")

    # Filter and score jobs
    filtered_jobs = filter_and_score_jobs_from_file()
    logger.info(
        f"Filtering done. {len(filtered_jobs)} jobs passed the threshold."
    )

    # Send jobs to email
    logger.info("Sending job listings via email...")
    if send_job_listings_email():
        logger.info("Email sent successfully.")
    else:
        logger.warning("Failed to send email.")

    # Run Telegram bot
    run_telegram = (
        input("Do you want to run the Telegram bot? (y/n): ").strip().lower()
    )
    if run_telegram == "y":
        logger.info("Starting Telegram bot...")
        logger.info("Use /stop inside the bot to stop the bot.")
        await dp.start_polling(bot)
    else:
        logger.info("Telegram bot was skipped by user.")


if __name__ == "__main__":
    asyncio.run(main())
