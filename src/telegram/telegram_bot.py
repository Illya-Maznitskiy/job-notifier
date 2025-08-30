import asyncio

from logs.logger import logger
from src.telegram.bot_config import dp, bot
from src.telegram.job_utils import notify_admin_startup

# THIS IMPORT IS CRITICAL to register command handlers!
# Register command handlers via module import
import src.telegram.commands.start_next  # noqa: F401
import src.telegram.commands.admin  # noqa: F401
import src.telegram.commands.keywords  # noqa: F401
import src.telegram.commands.refresh  # noqa: F401
import src.telegram.random_text  # noqa: F401


async def start_bot():
    """Start Telegram bot polling loop."""
    logger.info("-" * 60)
    logger.info("Starting bot polling...")

    # Notify the admin
    await notify_admin_startup()

    # Start polling
    await dp.start_polling(bot)
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    asyncio.run(start_bot())
