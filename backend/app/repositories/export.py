from sqlalchemy.orm import Session as DbSession

from app.models.driver import Driver
from app.models.lap import Lap
from app.models.meeting import Meeting
from app.models.pit_stop import PitStop
from app.models.position import Position
from app.models.session import Session as SessionModel
from app.models.session_result import SessionResult
from app.models.stint import Stint
from app.models.weather import Weather
from app.repositories import constructors as constructors_repo
from app.repositories import drivers as drivers_repo
from app.repositories.seasons import resolve_season

DRIVER_FIELDS = [
    "season",
    "position",
    "driver_number",
    "full_name",
    "name_acronym",
    "headshot_url",
    "country_code",
    "team_id",
    "team_name",
    "team_colour",
    "points",
    "wins",
    "podiums",
    "avg_finish",
    "dnf_rate",
]

CONSTRUCTOR_FIELDS = ["season", "position", "constructor_id", "name", "team_colour", "points", "wins", "podiums", "avg_finish", "dnf_rate"]

RACE_RESULT_FIELDS = [
    "meeting_name",
    "session_key",
    "session_name",
    "session_type",
    "driver_number",
    "driver_full_name",
    "position",
    "points",
    "dnf",
    "dns",
    "dsq",
]

LAP_FIELDS = [
    "session_key",
    "driver_number",
    "lap_number",
    "date_start",
    "lap_duration",
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3",
    "is_pit_out_lap",
]

PIT_STOP_FIELDS = ["session_key", "driver_number", "lap_number", "date", "pit_duration"]

STINT_FIELDS = ["session_key", "driver_number", "stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"]

WEATHER_FIELDS = ["session_key", "date", "air_temperature", "track_temperature", "humidity", "pressure", "rainfall", "wind_direction", "wind_speed"]

POSITION_FIELDS = ["session_key", "driver_number", "date", "position"]


def export_drivers(db: DbSession, year: int | None) -> list[dict]:
    _, rows = drivers_repo.list_drivers(db, year)
    return rows


def export_constructors(db: DbSession, year: int | None) -> list[dict]:
    _, rows = constructors_repo.list_constructors(db, year)
    return rows


def export_race_results(db: DbSession, year: int | None) -> list[dict]:
    season = resolve_season(db, year)
    rows = (
        db.query(
            Meeting.meeting_name.label("meeting_name"),
            SessionModel.session_key.label("session_key"),
            SessionModel.session_name.label("session_name"),
            SessionModel.session_type.label("session_type"),
            Driver.driver_number.label("driver_number"),
            Driver.full_name.label("driver_full_name"),
            SessionResult.position.label("position"),
            SessionResult.points.label("points"),
            SessionResult.dnf.label("dnf"),
            SessionResult.dns.label("dns"),
            SessionResult.dsq.label("dsq"),
        )
        .select_from(SessionResult)
        .join(SessionModel, SessionModel.id == SessionResult.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == SessionResult.driver_id)
        .filter(Meeting.season_id == season.id)
        .order_by(SessionModel.date_start.asc(), SessionResult.position.asc())
        .all()
    )
    return [dict(r._mapping) for r in rows]


def export_laps(db: DbSession, year: int | None, session_key: int | None) -> list[dict]:
    season = resolve_season(db, year)
    query = (
        db.query(
            SessionModel.session_key.label("session_key"),
            Driver.driver_number.label("driver_number"),
            Lap.lap_number.label("lap_number"),
            Lap.date_start.label("date_start"),
            Lap.lap_duration.label("lap_duration"),
            Lap.duration_sector_1.label("duration_sector_1"),
            Lap.duration_sector_2.label("duration_sector_2"),
            Lap.duration_sector_3.label("duration_sector_3"),
            Lap.is_pit_out_lap.label("is_pit_out_lap"),
        )
        .select_from(Lap)
        .join(SessionModel, SessionModel.id == Lap.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == Lap.driver_id)
        .filter(Meeting.season_id == season.id)
    )
    if session_key is not None:
        query = query.filter(SessionModel.session_key == session_key)
    rows = query.order_by(SessionModel.date_start.asc(), Driver.driver_number.asc(), Lap.lap_number.asc()).all()
    return [dict(r._mapping) for r in rows]


def export_pit_stops(db: DbSession, year: int | None, session_key: int | None) -> list[dict]:
    season = resolve_season(db, year)
    query = (
        db.query(
            SessionModel.session_key.label("session_key"),
            Driver.driver_number.label("driver_number"),
            PitStop.lap_number.label("lap_number"),
            PitStop.date.label("date"),
            PitStop.pit_duration.label("pit_duration"),
        )
        .select_from(PitStop)
        .join(SessionModel, SessionModel.id == PitStop.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == PitStop.driver_id)
        .filter(Meeting.season_id == season.id)
    )
    if session_key is not None:
        query = query.filter(SessionModel.session_key == session_key)
    rows = query.order_by(SessionModel.date_start.asc(), PitStop.lap_number.asc()).all()
    return [dict(r._mapping) for r in rows]


def export_stints(db: DbSession, year: int | None, session_key: int | None) -> list[dict]:
    season = resolve_season(db, year)
    query = (
        db.query(
            SessionModel.session_key.label("session_key"),
            Driver.driver_number.label("driver_number"),
            Stint.stint_number.label("stint_number"),
            Stint.lap_start.label("lap_start"),
            Stint.lap_end.label("lap_end"),
            Stint.compound.label("compound"),
            Stint.tyre_age_at_start.label("tyre_age_at_start"),
        )
        .select_from(Stint)
        .join(SessionModel, SessionModel.id == Stint.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == Stint.driver_id)
        .filter(Meeting.season_id == season.id)
    )
    if session_key is not None:
        query = query.filter(SessionModel.session_key == session_key)
    rows = query.order_by(SessionModel.date_start.asc(), Driver.driver_number.asc(), Stint.stint_number.asc()).all()
    return [dict(r._mapping) for r in rows]


def export_weather(db: DbSession, year: int | None, session_key: int | None) -> list[dict]:
    season = resolve_season(db, year)
    query = (
        db.query(
            SessionModel.session_key.label("session_key"),
            Weather.date.label("date"),
            Weather.air_temperature.label("air_temperature"),
            Weather.track_temperature.label("track_temperature"),
            Weather.humidity.label("humidity"),
            Weather.pressure.label("pressure"),
            Weather.rainfall.label("rainfall"),
            Weather.wind_direction.label("wind_direction"),
            Weather.wind_speed.label("wind_speed"),
        )
        .select_from(Weather)
        .join(SessionModel, SessionModel.id == Weather.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.season_id == season.id)
    )
    if session_key is not None:
        query = query.filter(SessionModel.session_key == session_key)
    rows = query.order_by(Weather.date.asc()).all()
    return [dict(r._mapping) for r in rows]


def export_positions(db: DbSession, year: int | None, session_key: int | None) -> list[dict]:
    season = resolve_season(db, year)
    query = (
        db.query(
            SessionModel.session_key.label("session_key"),
            Driver.driver_number.label("driver_number"),
            Position.date.label("date"),
            Position.position.label("position"),
        )
        .select_from(Position)
        .join(SessionModel, SessionModel.id == Position.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .join(Driver, Driver.id == Position.driver_id)
        .filter(Meeting.season_id == season.id)
    )
    if session_key is not None:
        query = query.filter(SessionModel.session_key == session_key)
    rows = query.order_by(Position.date.asc()).all()
    return [dict(r._mapping) for r in rows]


DATASETS: dict[str, tuple[list[str], bool]] = {
    # dataset name -> (fieldnames, accepts_session_key)
    "drivers": (DRIVER_FIELDS, False),
    "constructors": (CONSTRUCTOR_FIELDS, False),
    "race_results": (RACE_RESULT_FIELDS, False),
    "laps": (LAP_FIELDS, True),
    "pit_stops": (PIT_STOP_FIELDS, True),
    "stints": (STINT_FIELDS, True),
    "weather": (WEATHER_FIELDS, True),
    "positions": (POSITION_FIELDS, True),
}

_LOADERS = {
    "drivers": lambda db, year, session_key: export_drivers(db, year),
    "constructors": lambda db, year, session_key: export_constructors(db, year),
    "race_results": lambda db, year, session_key: export_race_results(db, year),
    "laps": export_laps,
    "pit_stops": export_pit_stops,
    "stints": export_stints,
    "weather": export_weather,
    "positions": export_positions,
}


def export_dataset(db: DbSession, dataset: str, year: int | None, session_key: int | None) -> tuple[list[str], list[dict]]:
    if dataset not in DATASETS:
        raise ValueError(f"Unknown dataset '{dataset}'")
    fieldnames, _ = DATASETS[dataset]
    rows = _LOADERS[dataset](db, year, session_key)
    return fieldnames, rows
