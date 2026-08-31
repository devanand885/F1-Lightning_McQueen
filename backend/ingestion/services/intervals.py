import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.interval import Interval
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_intervals(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_intervals(session_key)

    rows = []
    skipped = 0
    for record, raw in records:
        driver_id = driver_id_by_number.get(record.driver_number)
        if driver_id is None:
            skipped += 1
            continue
        gap_to_leader = record.gap_to_leader if isinstance(record.gap_to_leader, (int, float)) else None
        interval = record.interval if isinstance(record.interval, (int, float)) else None
        rows.append(
            {
                "session_id": session_id,
                "driver_id": driver_id,
                "date": record.date,
                "gap_to_leader": gap_to_leader,
                "interval": interval,
                "raw": raw,
            }
        )

    count = upsert(db, Interval, rows, ["session_id", "driver_id", "date"])
    if skipped:
        logger.warning("Session %s: skipped %d intervals for unrecognized driver_number", session_key, skipped)
    logger.info("Session %s: upserted %d intervals", session_key, count)
    return count
