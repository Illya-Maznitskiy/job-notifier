from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
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


class UserFilteredJob(Base):
    """Filtered job results for a user."""

    __tablename__ = "user_filtered_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uix_user_filtered_job"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    datetime_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    user: Mapped["User"] = relationship()
    job: Mapped["Job"] = relationship()
