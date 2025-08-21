from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


async def get_user_by_user_id(
    session: AsyncSession, user_id: int
) -> User | None:
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()


async def create_user(
    session: AsyncSession, user_id: int, username: str | None
) -> User:
    user = User(user_id=user_id, username=username)
    session.add(user)
    await session.flush()  # push changes to DB without committing
    await session.refresh(user)  # safe to refresh while transaction is open
    return user
