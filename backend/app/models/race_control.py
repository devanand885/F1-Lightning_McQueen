from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class RaceControlMessage(TimestampMixin, Base):
    __tablename__ = "race_control"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "date", "category", "message", name="uq_race_control_session_date_category_message"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    date: Mapped[datetime]
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), index=True)
    lap_number: Mapped[int | None]
    category: Mapped[str | None] = mapped_column(String(64))
    flag: Mapped[str | None]
    scope: Mapped[str | None]
    sector: Mapped[int | None]
    message: Mapped[str | None] = mapped_column(String(500))
