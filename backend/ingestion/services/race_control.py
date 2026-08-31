import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.race_control import RaceControlMessage
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_race_control(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_race_control(session_key)

    rows = []
    for record, _raw in records:
        driver_id = driver_id_by_number.get(record.driver_number) if record.driver_number is not None else None
        rows.append(
            {
                "session_id": session_id,
                "date": record.date,
                "driver_id": driver_id,
                "lap_number": record.lap_number,
                "category": record.category,
                "flag": record.flag,
                "scope": record.scope,
                "sector": record.sector,
                "message": (record.message or "")[:500] or None,
            }
        )

    count = upsert(db, RaceControlMessage, rows, ["session_id", "date", "category", "message"])
    logger.info("Session %s: upserted %d race control messages", session_key, count)
    return count
