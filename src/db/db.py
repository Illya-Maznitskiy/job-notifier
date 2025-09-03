import asyncio
import logging
import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from dotenv import load_dotenv


load_dotenv()


DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dbname")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # checks if a connection is alive before using it
    pool_recycle=1800,  # recycle connections every 30 minutes (seconds)
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield async DB session safely."""
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logging.error("Session creation failed:", e)


async def test_connection() -> None:
    """Test DB connection."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            logging.info("Test query result:", result.scalar())
    except Exception as e:
        logging.error("DB connection failed:", e)


if __name__ == "__main__":
    asyncio.run(test_connection())
