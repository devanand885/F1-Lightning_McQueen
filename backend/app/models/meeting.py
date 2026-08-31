from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Meeting(TimestampMixin, Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_key: Mapped[int] = mapped_column(unique=True, index=True)
    meeting_name: Mapped[str]
    meeting_official_name: Mapped[str | None]
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), index=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"), index=True)
    date_start: Mapped[datetime | None]
    gmt_offset: Mapped[str | None]

    season: Mapped["Season"] = relationship(back_populates="meetings")
    circuit: Mapped["Circuit"] = relationship(back_populates="meetings")
    sessions: Mapped[list["Session"]] = relationship(back_populates="meeting")
