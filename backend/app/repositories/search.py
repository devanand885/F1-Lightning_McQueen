from sqlalchemy.orm import Session as DbSession

from app.models.circuit import Circuit
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.meeting import Meeting
from app.models.session import Session as SessionModel


def _rank(text: str | None, query: str) -> int:
    text_lower = (text or "").lower()
    q = query.lower()
    if text_lower == q:
        return 0
    if text_lower.startswith(q):
        return 1
    return 2


def search(db: DbSession, q: str, limit_per_type: int = 8) -> list[dict]:
    like = f"%{q}%"
    results: list[dict] = []

    for driver in db.query(Driver).filter(Driver.full_name.ilike(like)).limit(limit_per_type).all():
        results.append(
            {
                "type": "driver",
                "id": driver.driver_number,
                "title": driver.full_name,
                "subtitle": driver.name_acronym,
                "_rank": _rank(driver.full_name, q),
            }
        )

    for constructor in db.query(Constructor).filter(Constructor.name.ilike(like)).limit(limit_per_type).all():
        results.append(
            {"type": "constructor", "id": constructor.id, "title": constructor.name, "subtitle": None, "_rank": _rank(constructor.name, q)}
        )

    for circuit in db.query(Circuit).filter(Circuit.circuit_short_name.ilike(like)).limit(limit_per_type).all():
        results.append(
            {
                "type": "circuit",
                "id": circuit.id,
                "title": circuit.circuit_short_name,
                "subtitle": circuit.location,
                "_rank": _rank(circuit.circuit_short_name, q),
            }
        )

    for meeting in db.query(Meeting).filter(Meeting.meeting_name.ilike(like)).limit(limit_per_type).all():
        results.append(
            {"type": "meeting", "id": meeting.id, "title": meeting.meeting_name, "subtitle": None, "_rank": _rank(meeting.meeting_name, q)}
        )

    for session in db.query(SessionModel).filter(SessionModel.session_name.ilike(like)).limit(limit_per_type).all():
        results.append(
            {
                "type": "session",
                "id": session.id,
                "title": session.session_name,
                "subtitle": session.session_type,
                "_rank": _rank(session.session_name, q),
            }
        )

    results.sort(key=lambda r: (r["_rank"], r["title"]))
    for r in results:
        r.pop("_rank")
    return results
