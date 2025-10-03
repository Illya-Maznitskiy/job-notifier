import asyncio
from datetime import datetime, timedelta, timezone

from logs.logger import logger
from src.utils.telegram.notifications import notify_inactive_users


async def notify_at_10am_daily() -> None:
    """Notify users daily at 10 AM UTC."""
    while True:
        now = datetime.now(timezone.utc)
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        logger.info(
            f"Waiting {hours}h {minutes}m "
            f"until next 10 AM UTC for notifications"
        )
        await asyncio.sleep(wait_seconds)

        try:
            await notify_inactive_users()
        except Exception as e:
            logger.error(f"Failed sending daily notifications: {e}")
