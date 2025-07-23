from logs.logger import logger
from notifier.telegram.telegram_bot import start_bot


async def run_telegram_bot(dp, bot):
    """Ask user and run Telegram bot if confirmed."""
    run_telegram = (
        input("Do you want to run the Telegram bot? (y/n): ").strip().lower()
    )

    if run_telegram == "y":
        logger.info("Starting Telegram bot...")
        logger.info("Use /stop inside the bot to stop the bot.")
        await start_bot()
    else:
        logger.info("Telegram bot was skipped by user.")
