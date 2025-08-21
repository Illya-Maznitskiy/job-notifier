from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserKeyword


async def get_user_keyword(
    session: AsyncSession, user_id: int, keyword: str
) -> UserKeyword | None:
    result = await session.execute(
        select(UserKeyword).where(
            UserKeyword.user_id == user_id,
            UserKeyword.keyword == keyword,
        )
    )
    return result.scalars().first()


async def upsert_user_keyword(
    session: AsyncSession, user_id: int, keyword: str, weight: int
) -> UserKeyword:
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


async def get_all_user_keywords(
    session: AsyncSession, user_id: int
) -> list[UserKeyword]:
    result = await session.execute(
        select(UserKeyword).where(UserKeyword.user_id == user_id)
    )
    return list(result.scalars().all())  # explicitly cast to list
