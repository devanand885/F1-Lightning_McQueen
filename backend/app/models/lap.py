from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Lap(TimestampMixin, Base):
    __tablename__ = "laps"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_laps_session_driver_lap"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    lap_number: Mapped[int]
    date_start: Mapped[datetime | None]
    lap_duration: Mapped[float | None]
    duration_sector_1: Mapped[float | None]
    duration_sector_2: Mapped[float | None]
    duration_sector_3: Mapped[float | None]
    is_pit_out_lap: Mapped[bool | None]
    i1_speed: Mapped[float | None]
    i2_speed: Mapped[float | None]
    st_speed: Mapped[float | None]
    # Verbatim OpenF1 record, in case future analysis needs a field the
    # structured columns above don't cover.
    raw: Mapped[dict | None] = mapped_column(JSONB)
