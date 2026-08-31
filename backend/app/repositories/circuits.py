from sqlalchemy import or_
from sqlalchemy.orm import Session as DbSession

from app.models.circuit import Circuit
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.meeting import Meeting
from app.models.season import Season
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry


def _seasons_by_circuit(db: DbSession) -> dict[int, list[int]]:
    rows = db.query(Meeting.circuit_id, Season.year).join(Season, Season.id == Meeting.season_id).distinct().all()
    result: dict[int, list[int]] = {}
    for circuit_id, year in rows:
        result.setdefault(circuit_id, []).append(year)
    for years in result.values():
        years.sort()
    return result


def list_circuits(db: DbSession, year: int | None, location: str | None) -> list[dict]:
    query = db.query(Circuit)
    if year is not None or location is not None:
        query = query.join(Meeting, Meeting.circuit_id == Circuit.id)
        if year is not None:
            query = query.join(Season, Season.id == Meeting.season_id).filter(Season.year == year)
        if location is not None:
            pattern = f"%{location}%"
            query = query.filter(or_(Circuit.location.ilike(pattern), Circuit.country_name.ilike(pattern)))
        query = query.distinct()

    circuits = query.order_by(Circuit.circuit_short_name.asc()).all()
    seasons_by_circuit = _seasons_by_circuit(db)

    return [
        {
            "circuit_id": c.id,
            "circuit_key": c.circuit_key,
            "circuit_short_name": c.circuit_short_name,
            "location": c.location,
            "country_name": c.country_name,
            "country_code": c.country_code,
            "seasons": seasons_by_circuit.get(c.id, []),
        }
        for c in circuits
    ]


def get_circuit(db: DbSession, circuit_id: int) -> dict | None:
    circuit = db.query(Circuit).filter(Circuit.id == circuit_id).one_or_none()
    if circuit is None:
        return None

    meetings = (
        db.query(Meeting.meeting_key, Meeting.meeting_name, Season.year, Meeting.date_start)
        .join(Season, Season.id == Meeting.season_id)
        .filter(Meeting.circuit_id == circuit_id)
        .order_by(Meeting.date_start.desc())
        .all()
    )

    drivers = (
        db.query(Driver.full_name)
        .join(SessionEntry, SessionEntry.driver_id == Driver.id)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.circuit_id == circuit_id)
        .distinct()
        .order_by(Driver.full_name.asc())
        .all()
    )

    constructors = (
        db.query(Constructor.name)
        .join(SessionEntry, SessionEntry.constructor_id == Constructor.id)
        .join(SessionModel, SessionModel.id == SessionEntry.session_id)
        .join(Meeting, Meeting.id == SessionModel.meeting_id)
        .filter(Meeting.circuit_id == circuit_id)
        .distinct()
        .order_by(Constructor.name.asc())
        .all()
    )

    return {
        "circuit_id": circuit.id,
        "circuit_key": circuit.circuit_key,
        "circuit_short_name": circuit.circuit_short_name,
        "location": circuit.location,
        "country_name": circuit.country_name,
        "country_code": circuit.country_code,
        "meetings": [{"meeting_key": m[0], "meeting_name": m[1], "season": m[2], "date_start": m[3]} for m in meetings],
        "drivers": [d[0] for d in drivers],
        "constructors": [c[0] for c in constructors],
    }
