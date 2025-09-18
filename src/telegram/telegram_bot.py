import asyncio

from logs.logger import logger
from src.telegram.bot_config import dp, bot
from src.telegram.job_utils import notify_admin_startup

# THIS IMPORT IS CRITICAL to register command handlers!
import src.telegram.commands.start_vacancy  # noqa: F401
import src.telegram.commands.admin  # noqa: F401
import src.telegram.commands.keywords.add_keywords  # noqa: F401
import src.telegram.commands.keywords.list_keywords  # noqa: F401
import src.telegram.commands.keywords.remove_keywords  # noqa: F401
import src.telegram.commands.refresh  # noqa: F401
import src.telegram.random_text  # noqa: F401
import src.telegram.commands.feedback  # noqa: F401
from src.utils.memory_logging import log_memory


async def start_bot() -> None:
    """Start Telegram bot polling loop."""
    logger.info("-" * 60)
    log_memory()
    logger.info("Starting bot...")

    try:
        # Notify the admin
        await notify_admin_startup()
        log_memory()

        # Start the bot
        await dp.start_polling(bot)
    except Exception as err:
        logger.exception(f"Bot crashed: {err}")
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except Exception as e:
        logger.exception(f"Unhandled error in start_bot(): {e}")
