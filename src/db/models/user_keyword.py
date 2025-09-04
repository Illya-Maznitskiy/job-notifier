from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

if TYPE_CHECKING:
    from src.db.models.user import User


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
