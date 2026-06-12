from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_place_id: Mapped[int] = mapped_column(
        ForeignKey("places.id"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    project_place: Mapped["Places"] = relationship(back_populates="notes")
