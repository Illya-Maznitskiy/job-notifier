from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    BigInteger,
    Date as SQLDate,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

# Imports for type checking only; prevents circular imports at runtime
if TYPE_CHECKING:
    from src.db.models.user_job import UserJob
    from src.db.models.user_keyword import UserKeyword


class User(Base):
    """Telegram user info."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(String(100), nullable=True)

    # daily limit tracking
    refresh_count: Mapped[int] = mapped_column(Integer, default=0)
    vacancies_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reset_date: Mapped[date] = mapped_column(SQLDate, default=None)

    jobs: Mapped[list["UserJob"]] = relationship(back_populates="user")
    keywords: Mapped[list["UserKeyword"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
