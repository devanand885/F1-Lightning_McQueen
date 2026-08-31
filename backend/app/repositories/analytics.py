"""Raw-row pulls shared by the DS/ML layer (ml/features/*).

Every function here returns plain lists of dicts (one row per lap/stint/etc,
matching the underlying table) already scoped to *completed* sessions - a
session counts as completed for a given driver iff there is a
`session_results` row for that (session_id, driver_id) pair. Future
scheduled sessions simply have no session_results rows yet, so this falls
out naturally without a date comparison.

Unlike the rest of the API (which defaults an omitted `season` to "the
latest ingested season"), these functions default to **pooling every
ingested season** - the DS/ML feature set is explicitly meant to use
"completed 2025 races + completed 2026 races" combined, not just the most
recent one. Pass `years=[2025]` etc. to scope to specific seasons instead.

No aggregation/statistics happen here - that's ml/features' job. This layer
only knows SQL, not numpy/pandas.
"""

from sqlalchemy import and_
from sqlalchemy.orm import Session as DbSession

from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.position import Position
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult
from app.models.stint import Stint
from app.models.weather import Weather


def _season_ids(db: DbSession, years: list[int] | None) -> list[int]:
    query = db.query(Season.id)
    if years is not None:
        query = query.filter(Season.year.in_(years))
    ids = [row[0] for row in query.all()]
    if not ids:
        raise ValueError(f"No ingested seasons match {years!r}")
    return ids


def drivers_all(db: DbSession) -> list[dict]:
    rows = db.query(Driver.id, Driver.driver_number, Driver.full_name).all()
    return [{"driver_id": r[0], "driver_number": r[1], "full_name": r[2]} for r in rows]


def usable_laps(db: DbSession, years: list[int] | None, session_type: str) -> list[dict]:
    """One row per usable lap (has a duration, not an in/out lap) in a
    completed session of the given type."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(
            Lap.session_id,
            Lap.driver_id,
            Lap.lap_number,
            Lap.date_start,
            Lap.lap_duration,
        )
        .select_from(Lap)
        .join(SessionModel, SessionModel.id == Lap.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Lap.session_id, SessionResult.driver_id == Lap.driver_id),
        )
        .filter(
            Meeting.season_id.in_(season_ids),
            SessionModel.session_type == session_type,
            Lap.lap_duration.isnot(None),
            Lap.is_pit_out_lap.isnot(True),
        )
        .all()
    )
    return [
        {"session_id": r[0], "driver_id": r[1], "lap_number": r[2], "date_start": r[3], "lap_duration": r[4]}
        for r in rows
    ]


def race_stints(db: DbSession, years: list[int] | None) -> list[dict]:
    season_ids = _season_ids(db, years)
    rows = (
        db.query(
            Stint.session_id,
            Stint.driver_id,
            Stint.stint_number,
            Stint.lap_start,
            Stint.lap_end,
            Stint.compound,
            Stint.tyre_age_at_start,
        )
        .select_from(Stint)
        .join(SessionModel, SessionModel.id == Stint.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Stint.session_id, SessionResult.driver_id == Stint.driver_id),
        )
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .all()
    )
    return [
        {
            "session_id": r[0],
            "driver_id": r[1],
            "stint_number": r[2],
            "lap_start": r[3],
            "lap_end": r[4],
            "compound": r[5],
            "tyre_age_at_start": r[6],
        }
        for r in rows
    ]


def race_positions_earliest(db: DbSession, years: list[int] | None) -> list[dict]:
    """The earliest recorded `positions` row per (session_id, driver_id) in
    completed race sessions - used as an early-race-position proxy."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(Position.session_id, Position.driver_id, Position.date, Position.position)
        .select_from(Position)
        .join(SessionModel, SessionModel.id == Position.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Position.session_id, SessionResult.driver_id == Position.driver_id),
        )
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .order_by(Position.session_id, Position.driver_id, Position.date.asc())
        .all()
    )
    earliest: dict[tuple[int, int], dict] = {}
    for session_id, driver_id, date, position in rows:
        key = (session_id, driver_id)
        if key not in earliest:
            earliest[key] = {"session_id": session_id, "driver_id": driver_id, "date": date, "position": position}
    return list(earliest.values())


def qualifying_classified_positions(db: DbSession, years: list[int] | None) -> list[dict]:
    """Final classified qualifying position per (session_id, driver_id) -
    used as the starting-grid proxy (real starting grid isn't ingested)."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(SessionResult.session_id, SessionResult.driver_id, SessionResult.position)
        .select_from(SessionResult)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(
            Meeting.season_id.in_(season_ids),
            SessionModel.session_type == "Qualifying",
            SessionResult.position.isnot(None),
        )
        .all()
    )
    return [{"session_id": r[0], "driver_id": r[1], "position": r[2]} for r in rows]


def race_weather(db: DbSession, years: list[int] | None) -> list[dict]:
    season_ids = _season_ids(db, years)
    rows = (
        db.query(Weather.session_id, Weather.date, Weather.rainfall)
        .select_from(Weather)
        .join(SessionModel, SessionModel.id == Weather.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .all()
    )
    return [{"session_id": r[0], "date": r[1], "rainfall": r[2]} for r in rows]


def race_weekend_entries(db: DbSession, years: list[int] | None) -> list[dict]:
    """driver<->constructor per session, excluding testing meetings - the
    same rule the ingestion layer uses to decide whether a session's team
    assignment is trustworthy (see ingestion/services/entries.py)."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(SessionEntry.session_id, SessionEntry.driver_id, SessionEntry.constructor_id)
        .select_from(SessionEntry)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id.in_(season_ids), Meeting.meeting_name.notilike("%testing%"))
        .all()
    )
    return [{"session_id": r[0], "driver_id": r[1], "constructor_id": r[2]} for r in rows]


def circuits_all(db: DbSession) -> list[dict]:
    rows = db.query(Circuit.id, Circuit.circuit_short_name).all()
    return [{"circuit_id": r[0], "circuit_short_name": r[1]} for r in rows]


def circuit_race_laps(db: DbSession, years: list[int] | None) -> list[dict]:
    """One row per usable race lap, with the circuit it was driven at
    attached - the raw material for circuit-type classification (field pace
    spread, top-speed-trap character)."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(
            Meeting.circuit_id,
            Lap.session_id,
            Lap.driver_id,
            Lap.lap_duration,
            Lap.st_speed,
        )
        .select_from(Lap)
        .join(SessionModel, SessionModel.id == Lap.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Lap.session_id, SessionResult.driver_id == Lap.driver_id),
        )
        .filter(
            Meeting.season_id.in_(season_ids),
            SessionModel.session_type == "Race",
            Lap.lap_duration.isnot(None),
            Lap.is_pit_out_lap.isnot(True),
        )
        .all()
    )
    return [
        {"circuit_id": r[0], "session_id": r[1], "driver_id": r[2], "lap_duration": r[3], "st_speed": r[4]}
        for r in rows
    ]


def circuit_race_stints(db: DbSession, years: list[int] | None) -> list[dict]:
    """One row per race stint, with the circuit it was driven at attached -
    used for the mean-stints-per-driver degradation-severity proxy."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(Meeting.circuit_id, Stint.session_id, Stint.driver_id, Stint.stint_number)
        .select_from(Stint)
        .join(SessionModel, SessionModel.id == Stint.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Stint.session_id, SessionResult.driver_id == Stint.driver_id),
        )
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .all()
    )
    return [
        {"circuit_id": r[0], "session_id": r[1], "driver_id": r[2], "stint_number": r[3]}
        for r in rows
    ]


def race_pit_stops(db: DbSession, years: list[int] | None) -> list[dict]:
    """One row per pit stop in a completed race session."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(PitStop.session_id, PitStop.driver_id, PitStop.lap_number, PitStop.date, PitStop.pit_duration)
        .select_from(PitStop)
        .join(SessionModel, SessionModel.id == PitStop.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == PitStop.session_id, SessionResult.driver_id == PitStop.driver_id),
        )
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .all()
    )
    return [
        {"session_id": r[0], "driver_id": r[1], "lap_number": r[2], "date": r[3], "pit_duration": r[4]} for r in rows
    ]


def race_positions_all(db: DbSession, years: list[int] | None) -> list[dict]:
    """Every recorded position sample in completed race sessions - used for
    pre/post pit-stop track-position comparisons (undercut analysis)."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(Position.session_id, Position.driver_id, Position.date, Position.position)
        .select_from(Position)
        .join(SessionModel, SessionModel.id == Position.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionResult,
            and_(SessionResult.session_id == Position.session_id, SessionResult.driver_id == Position.driver_id),
        )
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .all()
    )
    return [{"session_id": r[0], "driver_id": r[1], "date": r[2], "position": r[3]} for r in rows]


def session_context(db: DbSession, years: list[int] | None) -> list[dict]:
    """session_id -> circuit/meeting/date context, for any feature that
    needs to attach real-world labels (circuit type, meeting name, date) to
    a per-session pace/analytics figure - e.g. the driver-analytics
    pace-over-time trend and the circuit-type performance breakdown."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(
            SessionModel.id,
            SessionModel.session_type,
            SessionModel.date_start,
            Meeting.meeting_key,
            Meeting.meeting_name,
            Meeting.circuit_id,
        )
        .select_from(SessionModel)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id.in_(season_ids))
        .all()
    )
    return [
        {
            "session_id": r[0],
            "session_type": r[1],
            "date_start": r[2],
            "meeting_key": r[3],
            "meeting_name": r[4],
            "circuit_id": r[5],
        }
        for r in rows
    ]


def all_race_sessions(db: DbSession, year: int) -> list[dict]:
    """Every Race session for a season - including ones that haven't
    happened yet (no session_results rows). This is the source of truth for
    "how many races has this season got left", not `session_results_all`
    (which only ever sees completed sessions by construction)."""
    season_ids = _season_ids(db, [year])
    rows = (
        db.query(SessionModel.id, Meeting.meeting_key, Meeting.meeting_name, SessionModel.date_start)
        .select_from(SessionModel)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id.in_(season_ids), SessionModel.session_type == "Race")
        .order_by(SessionModel.date_start.asc())
        .all()
    )
    return [{"session_id": r[0], "meeting_key": r[1], "meeting_name": r[2], "date_start": r[3]} for r in rows]


def current_driver_constructors(db: DbSession) -> list[dict]:
    """Each driver's most recent constructor, from the latest non-testing
    session_entries row by session date - the "who's on the current grid"
    signal used to decide who to simulate remaining races for. Session
    entries are session-scoped (a driver's team can change mid-season), so
    this is deliberately "most recent", not "first" or "most common"."""
    rows = (
        db.query(SessionEntry.driver_id, SessionEntry.constructor_id, SessionModel.date_start)
        .select_from(SessionEntry)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.meeting_name.notilike("%testing%"), SessionModel.date_start.isnot(None))
        .order_by(SessionEntry.driver_id, SessionModel.date_start.asc())
        .all()
    )
    latest: dict[int, dict] = {}
    for driver_id, constructor_id, date_start in rows:
        latest[driver_id] = {"driver_id": driver_id, "constructor_id": constructor_id, "date_start": date_start}
    return list(latest.values())


def session_results_all(db: DbSession, years: list[int] | None) -> list[dict]:
    """Every session_results row for the given seasons, with session_type
    attached - this is the master "was this session completed for this
    driver" signal and the source of DNF history / points / finishing
    position."""
    season_ids = _season_ids(db, years)
    rows = (
        db.query(
            SessionResult.session_id,
            SessionResult.driver_id,
            SessionModel.session_type,
            SessionModel.date_start,
            Meeting.meeting_key,
            SessionResult.position,
            SessionResult.points,
            SessionResult.dnf,
            SessionResult.dns,
            SessionResult.dsq,
        )
        .select_from(SessionResult)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id.in_(season_ids))
        .all()
    )
    return [
        {
            "session_id": r[0],
            "driver_id": r[1],
            "session_type": r[2],
            "date_start": r[3],
            "meeting_key": r[4],
            "position": r[5],
            "points": r[6],
            "dnf": r[7],
            "dns": r[8],
            "dsq": r[9],
        }
        for r in rows
    ]
