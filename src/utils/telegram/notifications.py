import random
from datetime import timedelta, date

from sqlalchemy import select

from logs.logger import logger
from src.db.db import AsyncSessionLocal
from src.db.models import User
from src.telegram.bot_config import (
    bot,
    NOTIFICATION_MESSAGES,
    NOTIFICATION_MEDIA,
)


async def send_notification(user: User) -> None:
    """Helper function for sending notification."""
    try:
        telegram_id = user.telegram_id
        msg = random.choice(NOTIFICATION_MESSAGES)
        media = random.choice(NOTIFICATION_MEDIA)

        await bot.send_animation(
            chat_id=telegram_id,
            animation=media,
            caption=msg,
        )

        user.last_notification_date = date.today()
        logger.info(f"Notification sent to user {telegram_id}")
    except Exception as e:
        logger.error(f"Failed sending notification: {e}")


async def notify_inactive_users(days: int = 3) -> None:
    """Notify without notification and inactive users for 'days' days."""
    cutoff: date = date.today() - timedelta(days=days)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            for user in users:
                if not user.last_notification_date:
                    await send_notification(user)

                elif user.last_notification_date < date.today():
                    # check if user was active last days
                    if user.last_reset_date > cutoff:
                        await send_notification(user)

            await session.commit()
    except Exception as e:
        logger.error(f"DB or session error: {e}")
