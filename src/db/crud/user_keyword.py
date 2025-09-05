from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from logs.logger import logger
from src.db.models.user_keyword import UserKeyword


async def get_user_keyword(
    session: AsyncSession, user_id: int, keyword: str
) -> UserKeyword | None:
    """Fetch a specific keyword for a user."""
    try:
        result = await session.execute(
            select(UserKeyword).where(
                UserKeyword.user_id == user_id,
                UserKeyword.keyword == keyword,
            )
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(
            f"Failed to fetch keyword '{keyword}' for user {user_id}: {e}"
        )
        return None


async def upsert_user_keyword(
    session: AsyncSession, user_id: int, keyword: str, weight: int
) -> UserKeyword | None:
    """Insert or update a user's keyword."""
    try:
        existing_kw = await get_user_keyword(session, user_id, keyword)
        if existing_kw:
            existing_kw.weight = weight
            await session.flush()
            await session.refresh(existing_kw)
            return existing_kw

        new_kw = UserKeyword(user_id=user_id, keyword=keyword, weight=weight)
        session.add(new_kw)
        await session.flush()
        await session.refresh(new_kw)
        return new_kw
    except Exception as e:
        logger.error(
            f"Failed to upsert keyword '{keyword}' for user {user_id}: {e}"
        )
        return None


async def get_user_all_keywords(
    session: AsyncSession, user_id: int
) -> list[UserKeyword]:
    """Fetch all keywords for a user."""
    try:
        result = await session.execute(
            select(UserKeyword).where(UserKeyword.user_id == user_id)
        )
        return list(result.scalars().all())
    except Exception as e:
        logger.error(f"Failed to fetch all keywords for user {user_id}: {e}")
        return []


async def delete_user_keyword(
    session: AsyncSession, user_id: int, keyword: str
) -> bool:
    """Delete a keyword for a user."""
    try:
        existing_kw = await get_user_keyword(session, user_id, keyword)
        if existing_kw:
            await session.delete(existing_kw)
            await session.flush()
            return True
        return False
    except Exception as e:
        logger.error(
            f"Failed to delete keyword '{keyword}' for user {user_id}: {e}"
        )
        return False
