import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.integrations.openf1.schemas import SessionRecord
from app.models.session import Session as SessionModel
from ingestion.services.meetings import ensure_meeting

logger = logging.getLogger(__name__)


def upsert_session_from_record(db: DbSession, meeting_id: int, record: SessionRecord) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.session_key == record.session_key).one_or_none()
    if session is None:
        session = SessionModel(session_key=record.session_key)
        db.add(session)

    session.meeting_id = meeting_id
    session.session_name = record.session_name
    session.session_type = record.session_type
    session.date_start = record.date_start
    session.date_end = record.date_end
    session.gmt_offset = record.gmt_offset
    db.flush()
    return session


def ensure_session(client: OpenF1Client, db: DbSession, session_key: int) -> SessionModel:
    """Fetch and upsert a single session (and its meeting/circuit/season)
    without touching its lap/position/etc. data."""
    records = client.get_sessions(session_key=session_key)
    if not records:
        raise ValueError(f"OpenF1 returned no session for session_key={session_key}")
    record, _raw = records[0]
    meeting = ensure_meeting(client, db, record.meeting_key)
    session = upsert_session_from_record(db, meeting.id, record)
    logger.info("Ensured session %s (%s)", session.session_key, session.session_name)
    return session
