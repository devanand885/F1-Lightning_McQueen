import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.integrations.openf1.schemas import MeetingRecord
from app.models.meeting import Meeting
from ingestion.services.circuits import upsert_circuit
from ingestion.services.seasons import upsert_season

logger = logging.getLogger(__name__)


def upsert_meeting_from_record(db: DbSession, record: MeetingRecord) -> Meeting:
    season = upsert_season(db, record.year)
    circuit = upsert_circuit(db, record)

    meeting = db.query(Meeting).filter(Meeting.meeting_key == record.meeting_key).one_or_none()
    if meeting is None:
        meeting = Meeting(meeting_key=record.meeting_key)
        db.add(meeting)

    meeting.meeting_name = record.meeting_name
    meeting.meeting_official_name = record.meeting_official_name
    meeting.season_id = season.id
    meeting.circuit_id = circuit.id
    meeting.date_start = record.date_start
    meeting.gmt_offset = record.gmt_offset
    db.flush()
    return meeting


def ensure_meeting(client: OpenF1Client, db: DbSession, meeting_key: int) -> Meeting:
    """Fetch and upsert a single meeting (and its season/circuit) without
    touching its sessions."""
    records = client.get_meetings(meeting_key=meeting_key)
    if not records:
        raise ValueError(f"OpenF1 returned no meeting for meeting_key={meeting_key}")
    record, _raw = records[0]
    meeting = upsert_meeting_from_record(db, record)
    logger.info("Ensured meeting %s (%s)", meeting.meeting_key, meeting.meeting_name)
    return meeting
