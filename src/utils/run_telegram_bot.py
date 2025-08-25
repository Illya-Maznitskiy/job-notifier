from logs.logger import logger
from src.telegram import start_bot


async def run_telegram_bot(dp, bot):
    """Run Telegram bot."""
    try:
        logger.info("Starting Telegram bot...")
        logger.info("Use /stop inside the bot to stop the bot.")
        await start_bot()
    except Exception as e:
        logger.error(f"Error while running Telegram bot: {e}", exc_info=True)
