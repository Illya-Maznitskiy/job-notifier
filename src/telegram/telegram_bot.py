import asyncio

from logs.logger import logger
from src.telegram.bot_config import dp, bot
from src.telegram.job_utils import notify_admin_startup

# THIS IMPORT IS CRITICAL to register command handlers!
from src.telegram.commands.start_next import (  # noqa: F401
    cmd_start,
    send_next_vacancy,
)
from src.telegram.commands.admin import cmd_stop  # noqa: F401

from src.telegram.commands.keywords import add_keyword  # noqa: F401
from src.telegram.commands.refresh import refresh_jobs  # noqa: F401
from src.telegram.random_text import handle_random_text  # noqa: F401


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
