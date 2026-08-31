import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.session_result import SessionResult
from ingestion.services.upsert import upsert

logger = logging.getLogger(__name__)


def ingest_session_results(
    client: OpenF1Client, db: DbSession, session_key: int, session_id: int, driver_id_by_number: dict[int, int]
) -> int:
    records = client.get_session_result(session_key)

    rows = []
    skipped = 0
    for record, raw in records:
        driver_id = driver_id_by_number.get(record.driver_number)
        if driver_id is None:
            skipped += 1
            continue
        # `duration` is a single number for race-style sessions but a list of
        # per-segment values (Q1/Q2/Q3) for qualifying - only the simple case
        # is stored in the structured column, the full value is kept in `raw`.
        duration = record.duration if isinstance(record.duration, (int, float)) else None
        gap_to_leader = record.gap_to_leader if isinstance(record.gap_to_leader, (str, int, float)) else None
        gap_to_leader = None if gap_to_leader is None else str(gap_to_leader)
        rows.append(
            {
                "session_id": session_id,
                "driver_id": driver_id,
                "position": record.position,
                "number_of_laps": record.number_of_laps,
                "points": record.points,
                "dnf": record.dnf,
                "dns": record.dns,
                "dsq": record.dsq,
                "duration": duration,
                "gap_to_leader": gap_to_leader,
                "raw": raw,
            }
        )

    count = upsert(db, SessionResult, rows, ["session_id", "driver_id"])
    if skipped:
        logger.warning("Session %s: skipped %d results for unrecognized driver_number", session_key, skipped)
    logger.info("Session %s: upserted %d session results", session_key, count)
    return count
