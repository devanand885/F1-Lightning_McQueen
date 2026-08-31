from sqlalchemy.orm import Session as DbSession

from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult
from app.repositories.aggregation import aggregate_results
from app.repositories.seasons import resolve_season


def _results_rows(db: DbSession, season_id: int):
    return (
        db.query(SessionEntry.constructor_id, SessionModel.session_type, SessionResult.position, SessionResult.points, SessionResult.dnf)
        .select_from(SessionResult)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(
            SessionEntry,
            (SessionEntry.session_id == SessionResult.session_id) & (SessionEntry.driver_id == SessionResult.driver_id),
        )
        .filter(Meeting.season_id == season_id)
        .all()
    )


def _standings(db: DbSession, season_id: int) -> list[dict]:
    aggregates = aggregate_results(_results_rows(db, season_id))
    constructors = db.query(Constructor).filter(Constructor.id.in_(aggregates.keys())).all() if aggregates else []

    entries = []
    for constructor in constructors:
        entries.append({"constructor": constructor, **aggregates[constructor.id]})

    entries.sort(key=lambda e: (-e["points"], -e["wins"], e["constructor"].name))
    for position, entry in enumerate(entries, start=1):
        entry["position"] = position
    return entries


def list_constructors(db: DbSession, year: int | None) -> tuple[int, list[dict]]:
    season = resolve_season(db, year)
    entries = _standings(db, season.id)
    return season.year, [
        {
            "season": season.year,
            "position": e["position"],
            "constructor_id": e["constructor"].id,
            "name": e["constructor"].name,
            "team_colour": e["constructor"].team_colour,
            "points": e["points"],
            "wins": e["wins"],
            "podiums": e["podiums"],
            "avg_finish": e["avg_finish"],
            "dnf_rate": e["dnf_rate"],
        }
        for e in entries
    ]


def get_constructor(db: DbSession, constructor_id: int, year: int | None) -> dict | None:
    season = resolve_season(db, year)
    constructor = db.query(Constructor).filter(Constructor.id == constructor_id).one_or_none()
    if constructor is None:
        return None

    entries = _standings(db, season.id)
    entry = next((e for e in entries if e["constructor"].id == constructor.id), None)

    base = {
        "season": season.year,
        "constructor_id": constructor.id,
        "name": constructor.name,
        "name_acronym": constructor.name_acronym,
        "team_colour": constructor.team_colour,
    }
    if entry is None:
        return {
            **base,
            "position": None,
            "points": 0.0,
            "wins": 0,
            "podiums": 0,
            "avg_finish": None,
            "dnf_rate": None,
        }
    return {
        **base,
        "position": entry["position"],
        "points": entry["points"],
        "wins": entry["wins"],
        "podiums": entry["podiums"],
        "avg_finish": entry["avg_finish"],
        "dnf_rate": entry["dnf_rate"],
    }


def constructor_results(db: DbSession, constructor_id: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)

    rows = (
        db.query(
            SessionModel.session_key,
            SessionModel.session_name,
            SessionModel.session_type,
            Meeting.meeting_name,
            SessionModel.date_start,
            Driver.driver_number,
            Driver.full_name,
            SessionResult.position,
            SessionResult.points,
            SessionResult.dnf,
            SessionResult.dns,
            SessionResult.dsq,
        )
        .select_from(SessionResult)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == SessionResult.driver_id)
        .join(
            SessionEntry,
            (SessionEntry.session_id == SessionResult.session_id) & (SessionEntry.driver_id == SessionResult.driver_id),
        )
        .filter(Meeting.season_id == season.id, SessionEntry.constructor_id == constructor_id)
        .order_by(SessionModel.date_start.asc())
        .all()
    )
    return [
        {
            "session_key": r[0],
            "session_name": r[1],
            "session_type": r[2],
            "meeting_name": r[3],
            "date_start": r[4],
            "driver_number": r[5],
            "driver_full_name": r[6],
            "position": r[7],
            "points": r[8],
            "dnf": r[9],
            "dns": r[10],
            "dsq": r[11],
        }
        for r in rows
    ]


def constructor_drivers(db: DbSession, constructor_id: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)

    rows = (
        db.query(Driver)
        .join(SessionEntry, SessionEntry.driver_id == Driver.id)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season.id, SessionEntry.constructor_id == constructor_id)
        .distinct()
        .all()
    )
    return [
        {
            "driver_number": d.driver_number,
            "full_name": d.full_name,
            "name_acronym": d.name_acronym,
            "headshot_url": d.headshot_url,
        }
        for d in rows
    ]


def constructor_pit_stops(db: DbSession, constructor_id: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)

    rows = (
        db.query(
            SessionModel.session_key,
            SessionModel.session_type,
            Driver.driver_number,
            PitStop.lap_number,
            PitStop.date,
            PitStop.pit_duration,
        )
        .select_from(PitStop)
        .join(SessionModel, SessionModel.id == PitStop.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == PitStop.driver_id)
        .join(
            SessionEntry,
            (SessionEntry.session_id == PitStop.session_id) & (SessionEntry.driver_id == PitStop.driver_id),
        )
        .filter(Meeting.season_id == season.id, SessionEntry.constructor_id == constructor_id)
        .order_by(SessionModel.date_start.asc(), PitStop.lap_number.asc())
        .all()
    )
    return [
        {
            "session_key": r[0],
            "session_type": r[1],
            "driver_number": r[2],
            "lap_number": r[3],
            "date": r[4],
            "pit_duration": r[5],
        }
        for r in rows
    ]
