import logging
import random
from datetime import timedelta, date

from sqlalchemy import select

from src.db.db import AsyncSessionLocal
from src.db.models import User
from src.telegram.bot_config import bot, NOTIFICATION_MESSAGES


async def notify_inactive_users(days: int = 3) -> None:
    """Notify users inactive for 'days' days."""
    cutoff: date = date.today() - timedelta(days=days)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            for user in users:
                # check if notification wasn't sent today
                if (
                    not user.last_notification_date
                    or user.last_notification_date < date.today()
                ):
                    # check if user was active last days
                    if user.last_reset_date > cutoff:
                        try:
                            msg = random.choice(NOTIFICATION_MESSAGES)
                            await bot.send_message(user.chat_id, msg)
                            user.last_notification_date = date.today()
                            logging.info(
                                f"Notification sent to user {user.chat_id}"
                            )
                        except Exception as e:
                            logging.error(f"Failed sending notification: {e}")

            await session.commit()
    except Exception as e:
        logging.error(f"DB or session error: {e}")
