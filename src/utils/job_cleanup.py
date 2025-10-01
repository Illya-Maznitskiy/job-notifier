from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.config import ARCHIVE_LIFETIME_DAYS
from src.db.models.job import Job
from logs.logger import logger


async def delete_old_jobs(session: AsyncSession) -> None:
    """Delete jobs archived longer than configured period"""
    now = datetime.now(timezone.utc)
    try:
        result = await session.execute(
            delete(Job).where(Job.archived_at <= now)
        )
        deleted_count = result.rowcount or 0
        await session.commit()
        logger.info(
            f"Deleted {deleted_count} jobs archived"
            f" more than {ARCHIVE_LIFETIME_DAYS} days"
        )
    except Exception:
        await session.rollback()
        raise
