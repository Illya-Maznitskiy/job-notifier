from sqlalchemy import select, delete

from logs.logger import logger
from src.db.db import AsyncSessionLocal
from src.db.models import PendingUser


async def add_pending_user(user_id):
    """Add user to pending queue if not already present."""
    async with AsyncSessionLocal() as session:
        session.add(PendingUser(user_id=user_id))
        await session.commit()
    logger.info(f"Queued user {user_id}")


async def get_all_pending_users():
    """Return all users currently in the pending queue."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PendingUser))
        users = result.scalars().all()
    logger.info(f"Fetched {len(users)} pending users")
    return users


async def remove_pending_user(user_id):
    """Remove user from pending queue after processing."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(PendingUser).where(PendingUser.user_id == user_id)
        )
        await session.commit()
    logger.info(f"Removed user {user_id} from queue")
