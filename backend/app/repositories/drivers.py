from sqlalchemy.orm import Session as DbSession

from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from app.models.session_result import SessionResult
from app.repositories.aggregation import aggregate_results
from app.repositories.seasons import resolve_season


def _results_rows(db: DbSession, season_id: int):
    return (
        db.query(SessionResult.driver_id, SessionModel.session_type, SessionResult.position, SessionResult.points, SessionResult.dnf)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season_id)
        .all()
    )


def _current_teams(db: DbSession, season_id: int) -> dict[int, tuple[int, str, str | None]]:
    rows = (
        db.query(SessionEntry.driver_id, SessionEntry.constructor_id, Constructor.name, Constructor.team_colour)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Constructor, Constructor.id == SessionEntry.constructor_id)
        .filter(Meeting.season_id == season_id)
        .order_by(SessionModel.date_start.asc())
        .all()
    )
    teams: dict[int, tuple[int, str, str | None]] = {}
    for driver_id, constructor_id, name, colour in rows:
        teams[driver_id] = (constructor_id, name, colour)
    return teams


def _standings(db: DbSession, season_id: int) -> list[dict]:
    aggregates = aggregate_results(_results_rows(db, season_id))
    teams = _current_teams(db, season_id)

    drivers = db.query(Driver).filter(Driver.id.in_(aggregates.keys())).all() if aggregates else []

    entries = []
    for driver in drivers:
        agg = aggregates[driver.id]
        team_id, team_name, team_colour = teams.get(driver.id, (None, None, None))
        entries.append(
            {
                "driver": driver,
                "team_id": team_id,
                "team_name": team_name,
                "team_colour": team_colour,
                **agg,
            }
        )

    entries.sort(key=lambda e: (-e["points"], -e["wins"], e["driver"].full_name))
    for position, entry in enumerate(entries, start=1):
        entry["position"] = position
    return entries


def list_drivers(db: DbSession, year: int | None) -> tuple[int, list[dict]]:
    season = resolve_season(db, year)
    entries = _standings(db, season.id)
    return season.year, [
        {
            "season": season.year,
            "position": e["position"],
            "driver_number": e["driver"].driver_number,
            "full_name": e["driver"].full_name,
            "name_acronym": e["driver"].name_acronym,
            "headshot_url": e["driver"].headshot_url,
            "country_code": e["driver"].country_code,
            "team_id": e["team_id"],
            "team_name": e["team_name"],
            "team_colour": e["team_colour"],
            "points": e["points"],
            "wins": e["wins"],
            "podiums": e["podiums"],
            "avg_finish": e["avg_finish"],
            "dnf_rate": e["dnf_rate"],
        }
        for e in entries
    ]


def get_driver(db: DbSession, driver_number: int, year: int | None) -> dict | None:
    season = resolve_season(db, year)
    driver = db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()
    if driver is None:
        return None

    entries = _standings(db, season.id)
    entry = next((e for e in entries if e["driver"].id == driver.id), None)

    base = {
        "season": season.year,
        "driver_number": driver.driver_number,
        "full_name": driver.full_name,
        "first_name": driver.first_name,
        "last_name": driver.last_name,
        "name_acronym": driver.name_acronym,
        "broadcast_name": driver.broadcast_name,
        "headshot_url": driver.headshot_url,
        "country_code": driver.country_code,
    }
    if entry is None:
        return {
            **base,
            "position": None,
            "team_id": None,
            "team_name": None,
            "team_colour": None,
            "points": 0.0,
            "wins": 0,
            "podiums": 0,
            "avg_finish": None,
            "dnf_rate": None,
        }
    return {
        **base,
        "position": entry["position"],
        "team_id": entry["team_id"],
        "team_name": entry["team_name"],
        "team_colour": entry["team_colour"],
        "points": entry["points"],
        "wins": entry["wins"],
        "podiums": entry["podiums"],
        "avg_finish": entry["avg_finish"],
        "dnf_rate": entry["dnf_rate"],
    }


def driver_sessions(db: DbSession, driver_number: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)
    driver = db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()
    if driver is None:
        return []

    rows = (
        db.query(SessionModel.session_key, SessionModel.session_name, SessionModel.session_type, Meeting.meeting_name, SessionModel.date_start)
        .join(SessionEntry, SessionEntry.session_id == SessionModel.id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season.id, SessionEntry.driver_id == driver.id)
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
        }
        for r in rows
    ]


def driver_results(db: DbSession, driver_number: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)
    driver = db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()
    if driver is None:
        return []

    rows = (
        db.query(
            SessionModel.session_key,
            SessionModel.session_name,
            SessionModel.session_type,
            Meeting.meeting_name,
            SessionModel.date_start,
            SessionResult.position,
            SessionResult.points,
            SessionResult.dnf,
            SessionResult.dns,
            SessionResult.dsq,
        )
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season.id, SessionResult.driver_id == driver.id)
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
            "position": r[5],
            "points": r[6],
            "dnf": r[7],
            "dns": r[8],
            "dsq": r[9],
        }
        for r in rows
    ]


def driver_laps(db: DbSession, driver_number: int, session_key: int) -> list[dict]:
    driver = db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()
    if driver is None:
        return []

    rows = (
        db.query(Lap)
        .join(SessionModel, SessionModel.id == Lap.session_id)
        .filter(SessionModel.session_key == session_key, Lap.driver_id == driver.id)
        .order_by(Lap.lap_number.asc())
        .all()
    )
    return [
        {
            "lap_number": lap.lap_number,
            "date_start": lap.date_start,
            "lap_duration": lap.lap_duration,
            "duration_sector_1": lap.duration_sector_1,
            "duration_sector_2": lap.duration_sector_2,
            "duration_sector_3": lap.duration_sector_3,
            "is_pit_out_lap": lap.is_pit_out_lap,
        }
        for lap in rows
    ]


def driver_pit_stops(db: DbSession, driver_number: int, year: int | None) -> list[dict]:
    season = resolve_season(db, year)
    driver = db.query(Driver).filter(Driver.driver_number == driver_number).order_by(Driver.id.asc()).first()
    if driver is None:
        return []

    rows = (
        db.query(
            SessionModel.session_key, SessionModel.session_type, PitStop.lap_number, PitStop.date, PitStop.pit_duration
        )
        .join(SessionModel, SessionModel.id == PitStop.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season.id, PitStop.driver_id == driver.id)
        .order_by(SessionModel.date_start.asc(), PitStop.lap_number.asc())
        .all()
    )
    return [
        {"session_key": r[0], "session_type": r[1], "lap_number": r[2], "date": r[3], "pit_duration": r[4]} for r in rows
    ]
