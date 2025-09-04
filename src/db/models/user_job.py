from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.models.base import Base

# Imports for type checking only; prevents circular imports at runtime
if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.job import Job


class UserJob(Base):
    """Link between users and jobs with status."""

    __tablename__ = "user_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uix_user_job"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    datetime_sent: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    status: Mapped[str] = mapped_column(
        String(50), default="sent"
    )  # sent, skipped, applied

    user: Mapped["User"] = relationship(back_populates="jobs")
    job: Mapped["Job"] = relationship(back_populates="sent_to_users")
