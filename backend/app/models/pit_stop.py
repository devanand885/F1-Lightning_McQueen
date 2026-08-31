from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class PitStop(TimestampMixin, Base):
    __tablename__ = "pit_stops"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_pit_stops_session_driver_lap"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    lap_number: Mapped[int]
    date: Mapped[datetime | None]
    pit_duration: Mapped[float | None]
