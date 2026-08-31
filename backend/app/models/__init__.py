"""Import every model module so `Base.metadata` is fully populated for
Alembic autogenerate and `Base.metadata.create_all` in tests."""

from app.models.circuit import Circuit
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.interval import Interval
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.position import Position
from app.models.race_control import RaceControlMessage
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult
from app.models.stint import Stint
from app.models.weather import Weather

__all__ = [
    "Circuit",
    "Constructor",
    "Driver",
    "Interval",
    "Lap",
    "Meeting",
    "PitStop",
    "Position",
    "RaceControlMessage",
    "Season",
    "SessionModel",
    "SessionEntry",
    "SessionResult",
    "Stint",
    "Weather",
]
