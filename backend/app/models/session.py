from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Session(TimestampMixin, Base):
    """An F1 session (practice, qualifying, sprint, race, ...)."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_key: Mapped[int] = mapped_column(unique=True, index=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), index=True)
    session_name: Mapped[str]
    session_type: Mapped[str]
    date_start: Mapped[datetime | None]
    date_end: Mapped[datetime | None]
    gmt_offset: Mapped[str | None]

    meeting: Mapped["Meeting"] = relationship(back_populates="sessions")
