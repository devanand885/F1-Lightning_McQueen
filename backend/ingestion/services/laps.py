import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.lap import Lap
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_laps(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_laps(session_key)

    rows = []
    skipped = 0
    for record, raw in records:
        driver_id = driver_id_by_number.get(record.driver_number)
        if driver_id is None:
            skipped += 1
            continue
        rows.append(
            {
                "session_id": session_id,
                "driver_id": driver_id,
                "lap_number": record.lap_number,
                "date_start": record.date_start,
                "lap_duration": record.lap_duration,
                "duration_sector_1": record.duration_sector_1,
                "duration_sector_2": record.duration_sector_2,
                "duration_sector_3": record.duration_sector_3,
                "is_pit_out_lap": record.is_pit_out_lap,
                "i1_speed": record.i1_speed,
                "i2_speed": record.i2_speed,
                "st_speed": record.st_speed,
                "raw": raw,
            }
        )

    count = upsert(db, Lap, rows, ["session_id", "driver_id", "lap_number"])
    if skipped:
        logger.warning("Session %s: skipped %d laps for unrecognized driver_number", session_key, skipped)
    logger.info("Session %s: upserted %d laps", session_key, count)
    return count
