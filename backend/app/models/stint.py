from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Stint(TimestampMixin, Base):
    __tablename__ = "stints"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "stint_number", name="uq_stints_session_driver_stint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    stint_number: Mapped[int]
    lap_start: Mapped[int | None]
    lap_end: Mapped[int | None]
    compound: Mapped[str | None]
    tyre_age_at_start: Mapped[int | None]
