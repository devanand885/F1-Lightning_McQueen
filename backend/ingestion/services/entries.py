import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.integrations.openf1.schemas import DriverEntryRecord
from app.models.constructor import Constructor
from app.models.driver import Driver
from app.models.meeting import Meeting
from app.models.session import Session as SessionModel
from app.models.session_entry import SessionEntry
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def _upsert_driver(db: DbSession, record: DriverEntryRecord, trust_identity: bool) -> Driver:
    """Identity is keyed by full_name, not driver_number - pre-season
    testing sessions can report a driver under a different, non-standard car
    number, and keying by number would silently overwrite a different
    driver's row (this happened in practice; see the comment on the Driver
    model). `trust_identity=False` (testing sessions) still creates a
    missing row, but never overwrites an existing driver's fields."""
    driver = db.query(Driver).filter(Driver.full_name == record.full_name).one_or_none()
    if driver is None:
        driver = Driver(full_name=record.full_name)
        db.add(driver)
        trust_identity = True

    if trust_identity:
        driver.driver_number = record.driver_number
        driver.first_name = record.first_name
        driver.last_name = record.last_name
        driver.name_acronym = record.name_acronym
        driver.broadcast_name = record.broadcast_name
        driver.country_code = record.country_code
        driver.headshot_url = record.headshot_url
    db.flush()
    return driver


def _upsert_constructor(db: DbSession, record: DriverEntryRecord) -> Constructor:
    constructor = db.query(Constructor).filter(Constructor.name == record.team_name).one_or_none()
    if constructor is None:
        constructor = Constructor(name=record.team_name)
        db.add(constructor)

    constructor.team_colour = record.team_colour
    db.flush()
    return constructor


def _is_testing_session(db: DbSession, session_id: int) -> bool:
    meeting_name = (
        db.query(Meeting.meeting_name).join(SessionModel, SessionModel.meeting_id == Meeting.id).filter(SessionModel.id == session_id).scalar()
    )
    return "testing" in (meeting_name or "").lower()


def ingest_entries(client: OpenF1Client, db: DbSession, session_key: int, session_id: int) -> dict[int, int]:
    """Upserts drivers, constructors and session_entries for one session.

    Returns a {driver_number: driver_id} map that the other per-session-data
    ingestion services use to resolve foreign keys - valid for this session
    only, since driver_number is session-scoped, not a global identity.
    """
    records = client.get_drivers(session_key)
    trust_identity = not _is_testing_session(db, session_id)

    driver_id_by_number: dict[int, int] = {}
    entry_rows = []
    for record, _raw in records:
        driver = _upsert_driver(db, record, trust_identity)
        constructor = _upsert_constructor(db, record)
        driver_id_by_number[record.driver_number] = driver.id
        entry_rows.append(
            {
                "session_id": session_id,
                "driver_id": driver.id,
                "constructor_id": constructor.id,
                "team_colour": record.team_colour,
                "headshot_url": record.headshot_url,
            }
        )

    count = upsert(db, SessionEntry, entry_rows, ["session_id", "driver_id"])
    logger.info("Session %s: upserted %d driver entries", session_key, count)
    return driver_id_by_number
