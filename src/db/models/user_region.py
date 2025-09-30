from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class UserRegion(Base):
    """User selected region for job search."""

    __tablename__ = "user_regions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    region = Column(String, nullable=False)

    user = relationship("User", back_populates="regions")
