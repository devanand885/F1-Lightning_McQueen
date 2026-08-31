from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class SessionResult(TimestampMixin, Base):
    __tablename__ = "session_results"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", name="uq_session_results_session_driver"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    position: Mapped[int | None]
    number_of_laps: Mapped[int | None]
    points: Mapped[float | None]
    dnf: Mapped[bool | None]
    dns: Mapped[bool | None]
    dsq: Mapped[bool | None]
    duration: Mapped[float | None]
    gap_to_leader: Mapped[str | None]
    # OpenF1 returns `duration`/`gap_to_leader` as a list of per-segment
    # values for qualifying sessions (Q1/Q2/Q3). The structured columns
    # above hold the race/simple case; the full record is kept here too.
    raw: Mapped[dict | None] = mapped_column(JSONB)
