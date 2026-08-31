import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.stint import Stint
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_stints(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_stints(session_key)

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
                "stint_number": record.stint_number,
                "lap_start": record.lap_start,
                "lap_end": record.lap_end,
                "compound": record.compound,
                "tyre_age_at_start": record.tyre_age_at_start,
            }
        )

    count = upsert(db, Stint, rows, ["session_id", "driver_id", "stint_number"])
    if skipped:
        logger.warning("Session %s: skipped %d stints for unrecognized driver_number", session_key, skipped)
    logger.info("Session %s: upserted %d stints", session_key, count)
    return count
