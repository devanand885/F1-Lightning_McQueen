import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.pit_stop import PitStop
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_pit_stops(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_pit_stops(session_key)

    rows = []
    skipped = 0
    for record, _raw in records:
        driver_id = driver_id_by_number.get(record.driver_number)
        if driver_id is None:
            skipped += 1
            continue
        rows.append(
            {
                "session_id": session_id,
                "driver_id": driver_id,
                "lap_number": record.lap_number,
                "date": record.date,
                "pit_duration": record.pit_duration,
            }
        )

    count = upsert(db, PitStop, rows, ["session_id", "driver_id", "lap_number"])
    if skipped:
        logger.warning("Session %s: skipped %d pit stops for unrecognized driver_number", session_key, skipped)
    logger.info("Session %s: upserted %d pit stops", session_key, count)
    return count
