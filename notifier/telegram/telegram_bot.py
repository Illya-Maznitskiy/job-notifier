import asyncio

from logs.logger import logger
from notifier.telegram.bot_config import dp, bot

# THIS IMPORT IS CRITICAL to register handlers!
from notifier.telegram import commands


async def main():
    """Start Telegram bot polling loop."""
    logger.info("-" * 60)
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    asyncio.run(main())
