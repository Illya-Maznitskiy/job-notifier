from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    BigInteger,
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
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)

    jobs: Mapped[list["UserJob"]] = relationship(back_populates="user")
    keywords: Mapped[list["UserKeyword"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
