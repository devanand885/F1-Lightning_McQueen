from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Circuit(TimestampMixin, Base):
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_key: Mapped[int] = mapped_column(unique=True, index=True)
    circuit_short_name: Mapped[str]
    location: Mapped[str | None]
    country_name: Mapped[str | None]
    country_code: Mapped[str | None]

    meetings: Mapped[list["Meeting"]] = relationship(back_populates="circuit")
