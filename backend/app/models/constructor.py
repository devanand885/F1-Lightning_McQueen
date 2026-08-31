from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Constructor(TimestampMixin, Base):
    """Derived from the distinct team_name/team_colour values seen on OpenF1
    driver entries - OpenF1 has no dedicated constructors endpoint."""

    __tablename__ = "constructors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    name_acronym: Mapped[str | None]
    team_colour: Mapped[str | None]
