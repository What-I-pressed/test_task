from typing import List

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class Places(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    external_place_id: Mapped[str] = mapped_column(String, nullable=False)
    visited: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped["Project"] = relationship(back_populates="places")
    notes: Mapped[List["Note"]] = relationship(
        back_populates="project_place",
        cascade="all, delete-orphan",
    )
