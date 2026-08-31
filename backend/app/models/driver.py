from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Driver(TimestampMixin, Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Not unique: OpenF1 reports non-standard car numbers during pre-season
    # testing (e.g. a driver's real-season number swapped for a promotional
    # one), so driver_number can't be trusted as a stable global identity
    # key - full_name is. This is just the most-recently-seen number from a
    # non-testing session (see ingestion/services/entries.py).
    driver_number: Mapped[int] = mapped_column(index=True)
    full_name: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    name_acronym: Mapped[str | None]
    broadcast_name: Mapped[str | None]
    country_code: Mapped[str | None]
    headshot_url: Mapped[str | None]
