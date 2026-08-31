from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Weather(TimestampMixin, Base):
    __tablename__ = "weather"
    __table_args__ = (UniqueConstraint("session_id", "date", name="uq_weather_session_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    date: Mapped[datetime]
    air_temperature: Mapped[float | None]
    track_temperature: Mapped[float | None]
    humidity: Mapped[float | None]
    pressure: Mapped[float | None]
    rainfall: Mapped[float | None]
    wind_direction: Mapped[float | None]
    wind_speed: Mapped[float | None]
