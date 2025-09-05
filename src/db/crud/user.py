from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from logs.logger import logger
from src.db.models.user import User


async def get_user_by_user_id(
    session: AsyncSession, user_id: int
) -> User | None:
    """Fetch a User by user_id."""
    try:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        return None


async def create_user(
    session: AsyncSession, user_id: int, username: str | None
) -> User | None:
    """Create and save a new User."""
    try:
        user = User(user_id=user_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except Exception as e:
        logger.error(f"Failed to create user {user_id}: {e}")
        return None
