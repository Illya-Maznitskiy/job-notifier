from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ARRAY,
    Text,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

# Imports for type checking only; prevents circular imports at runtime
if TYPE_CHECKING:
    from src.db.models.user_job import UserJob


class Job(Base):
    """Scraped job listings."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    sent_to_users: Mapped[list["UserJob"]] = relationship(back_populates="job")
