from datetime import UTC, datetime

from sqlalchemy.orm import Session as DbSession

from app.models.meeting import Meeting
from app.models.session import Session as SessionModel
from app.repositories.seasons import resolve_season


def _now_naive_utc() -> datetime:
    # Columns are naive UTC (OpenF1 always reports UTC-offset timestamps).
    return datetime.now(UTC).replace(tzinfo=None)


def season_overview(db: DbSession, year: int | None) -> dict:
    season = resolve_season(db, year)

    meeting_count = db.query(Meeting).filter(Meeting.season_id == season.id).count()
    session_count = (
        db.query(SessionModel).join(Meeting, Meeting.id == SessionModel.meeting_id).filter(Meeting.season_id == season.id).count()
    )

    now = _now_naive_utc()
    last_completed = (
        db.query(Meeting)
        .filter(Meeting.season_id == season.id, Meeting.date_start <= now)
        .order_by(Meeting.date_start.desc())
        .first()
    )
    next_meeting = (
        db.query(Meeting)
        .filter(Meeting.season_id == season.id, Meeting.date_start > now)
        .order_by(Meeting.date_start.asc())
        .first()
    )

    return {
        "season": season.year,
        "meeting_count": meeting_count,
        "session_count": session_count,
        "last_completed_meeting": last_completed.meeting_name if last_completed else None,
        "next_meeting": next_meeting.meeting_name if next_meeting else None,
    }


def calendar(db: DbSession, year: int | None) -> list[dict]:
    season = resolve_season(db, year)
    now = _now_naive_utc()

    meetings = db.query(Meeting).filter(Meeting.season_id == season.id).order_by(Meeting.date_start.asc()).all()
    return [
        {
            "meeting_key": m.meeting_key,
            "meeting_name": m.meeting_name,
            "circuit_short_name": m.circuit.circuit_short_name,
            "location": m.circuit.location,
            "date_start": m.date_start,
            "status": "completed" if m.date_start and m.date_start <= now else "upcoming",
        }
        for m in meetings
    ]
