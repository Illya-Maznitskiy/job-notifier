from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    ARRAY,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Base model for all tables."""

    pass


class User(Base):
    """Telegram user info."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)

    jobs: Mapped[list["UserJob"]] = relationship(back_populates="user")
    keywords: Mapped[list["UserKeyword"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Job(Base):
    """Scraped job listings."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # salary can be null or string
    skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )  # PostgreSQL array
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    sent_to_users: Mapped[list["UserJob"]] = relationship(back_populates="job")


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
        DateTime, default=datetime.utcnow
    )
    status: Mapped[str] = mapped_column(
        String(50), default="sent"
    )  # sent, skipped, applied

    user: Mapped["User"] = relationship(back_populates="jobs")
    job: Mapped["Job"] = relationship(back_populates="sent_to_users")


class UserKeyword(Base):
    """Keywords for each user with weights."""

    __tablename__ = "user_keywords"
    __table_args__ = (
        UniqueConstraint("user_id", "keyword", name="uix_user_keyword"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # positive or negative

    user: Mapped["User"] = relationship(back_populates="keywords")


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
        DateTime, default=datetime.utcnow
    )

    user: Mapped["User"] = relationship()
    job: Mapped["Job"] = relationship()
