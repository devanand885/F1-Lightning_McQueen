"""DB-side support for the historical telemetry replay feature.

This module only ever reads tables that are already ingested (sessions,
meetings, drivers, session_entries, laps, positions) - it never touches
OpenF1 and nothing it returns is telemetry. High-frequency `location`/
`car_data` telemetry is fetched on demand by app/services/replay_service.py
and is never written to Postgres (see that module's docstring for why).
"""

from datetime import datetime

from sqlalchemy.orm import Session as DbSession

from app.models.circuit import Circuit
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.position import Position
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult


def list_completed_race_sessions(db: DbSession) -> list[dict]:
    """Every completed main-race session, grouped for the race picker.
    "Completed" matches the definition already used across the app: has at
    least one session_results row - a future-scheduled race simply has none
    yet.

    Filters on `session_name == "Race"`, not just `session_type == "Race"`:
    OpenF1 tags a Sprint session's `session_type` as "Race" too (only
    `session_name` distinguishes "Sprint" from "Race" - confirmed against
    the ingested 2025 Chinese GP, which has both under session_type
    "Race"). Without this, a sprint weekend would show the same meeting
    name twice in the picker with no way to tell which entry is which -
    excluding Sprint here keeps the picker to exactly the "main Race
    session" the feature is scoped to."""
    rows = (
        db.query(
            SessionModel.session_key,
            SessionModel.date_start,
            Meeting.meeting_name,
            Circuit.circuit_short_name,
            Season.year,
        )
        .select_from(SessionModel)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Season, Season.id == Meeting.season_id)
        .join(Circuit, Circuit.id == Meeting.circuit_id)
        .filter(
            SessionModel.session_type == "Race",
            SessionModel.session_name == "Race",
            SessionModel.id.in_(db.query(SessionResult.session_id).distinct()),
        )
        .order_by(Season.year.desc(), SessionModel.date_start.desc())
        .all()
    )
    return [
        {
            "session_key": r[0],
            "date_start": r[1],
            "meeting_name": r[2],
            "circuit_short_name": r[3],
            "season": r[4],
        }
        for r in rows
    ]


def get_session_by_key(db: DbSession, session_key: int) -> SessionModel | None:
    return db.query(SessionModel).filter(SessionModel.session_key == session_key).one_or_none()


def get_race_time_bounds(db: DbSession, session_id: int) -> tuple[datetime, datetime] | None:
    """The real start/end of race running for this session, derived from
    ingested lap timestamps - deliberately not the raw OpenF1 session window,
    which also covers grid formation and post-race data we don't want to
    fetch or replay."""
    row = (
        db.query(Lap.date_start)
        .filter(Lap.session_id == session_id, Lap.date_start.isnot(None))
        .order_by(Lap.date_start.asc())
        .first()
    )
    last = (
        db.query(Lap.date_start)
        .filter(Lap.session_id == session_id, Lap.date_start.isnot(None))
        .order_by(Lap.date_start.desc())
        .first()
    )
    if row is None or last is None:
        return None
    return row[0], last[0]


def get_session_entries(db: DbSession, session_id: int) -> list[dict]:
    """driver_number/name/constructor for every driver entered in this
    session - the identity + team-colour source for the replay, keyed the
    same way OpenF1's location/car_data telemetry keys its rows
    (driver_number)."""
    rows = (
        db.query(
            Driver.driver_number,
            Driver.full_name,
            Driver.name_acronym,
            Constructor.name,
            SessionEntry.team_colour,
        )
        .select_from(SessionEntry)
        .join(Driver, Driver.id == SessionEntry.driver_id)
        .join(Constructor, Constructor.id == SessionEntry.constructor_id)
        .filter(SessionEntry.session_id == session_id)
        .all()
    )
    return [
        {
            "driver_number": r[0],
            "full_name": r[1],
            "name_acronym": r[2],
            "constructor_name": r[3],
            "team_colour": r[4],
        }
        for r in rows
    ]


def get_laps_for_replay(db: DbSession, session_id: int) -> list[dict]:
    """driver_number + lap boundaries for this session - used to attach a
    real lap number to each replay frame and to pick a reference driver's
    fastest lap for deriving the circuit outline."""
    rows = (
        db.query(Driver.driver_number, Lap.lap_number, Lap.date_start, Lap.lap_duration)
        .select_from(Lap)
        .join(Driver, Driver.id == Lap.driver_id)
        .filter(Lap.session_id == session_id, Lap.date_start.isnot(None))
        .order_by(Driver.driver_number, Lap.lap_number)
        .all()
    )
    return [{"driver_number": r[0], "lap_number": r[1], "date_start": r[2], "lap_duration": r[3]} for r in rows]


def get_positions_for_replay(db: DbSession, session_id: int) -> list[dict]:
    """driver_number + position-over-time for this session - used to
    synchronize the live leaderboard to the current replay timestamp
    instead of showing the final classification throughout."""
    rows = (
        db.query(Driver.driver_number, Position.date, Position.position)
        .select_from(Position)
        .join(Driver, Driver.id == Position.driver_id)
        .filter(Position.session_id == session_id)
        .order_by(Driver.driver_number, Position.date)
        .all()
    )
    return [{"driver_number": r[0], "date": r[1], "position": r[2]} for r in rows]
