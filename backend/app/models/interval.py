from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Interval(TimestampMixin, Base):
    __tablename__ = "intervals"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", "date", name="uq_intervals_session_driver_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    date: Mapped[datetime]
    # Null when OpenF1 reports a lapped car ("+4 LAPS") instead of a gap in
    # seconds - the original value is preserved in `raw`.
    gap_to_leader: Mapped[float | None]
    interval: Mapped[float | None]
    raw: Mapped[dict | None] = mapped_column(JSONB)
