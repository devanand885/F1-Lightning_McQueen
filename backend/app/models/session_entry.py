from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class SessionEntry(TimestampMixin, Base):
    """A driver's entry (car + team) in a specific session - mirrors the
    OpenF1 /drivers endpoint, which is session-scoped."""

    __tablename__ = "session_entries"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", name="uq_session_entries_session_driver"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructors.id"), index=True)
    team_colour: Mapped[str | None]
    headshot_url: Mapped[str | None]
