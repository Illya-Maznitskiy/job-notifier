from logs.logger import logger


async def run_telegram_bot(dp, bot):
    """Ask user and run Telegram bot if confirmed."""
    run_telegram = (
        input("Do you want to run the Telegram bot? (y/n): ").strip().lower()
    )

    if run_telegram == "y":
        logger.info("Starting Telegram bot...")
        logger.info("Use /stop inside the bot to stop the bot.")
        await dp.start_polling(bot)
    else:
        logger.info("Telegram bot was skipped by user.")
