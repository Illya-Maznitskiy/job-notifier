from sqlalchemy import select, delete

from logs.logger import logger
from src.db.db import AsyncSessionLocal
from src.db.models import PendingUser


async def add_pending_user(user_id, command):
    """Add user+command to pending queue if not already present."""
    async with AsyncSessionLocal() as session:
        session.add(PendingUser(user_id=user_id, command=command))
        await session.commit()
    logger.info(f"Queued user {user_id} for command '{command}'")


async def get_all_pending_users():
    """Return all users and commands currently in the pending queue."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PendingUser))
        users = result.scalars().all()
    logger.info(f"Fetched {len(users)} pending users")
    return users


async def remove_pending_user(user_id, command=None):
    """Remove user (and optionally command) from pending queue after processing."""
    async with AsyncSessionLocal() as session:
        query = delete(PendingUser).where(PendingUser.user_id == user_id)
        if command:
            query = query.where(PendingUser.command == command)
        await session.execute(query)
        await session.commit()
    logger.info(f"Removed user {user_id} from queue for command '{command}'")
