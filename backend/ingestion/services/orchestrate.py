"""Composes the smaller per-entity services into season/meeting/session
level ingestion runs. Every step commits independently and failures are
logged and skipped rather than aborting the whole run."""

import logging

from sqlalchemy.orm import Session as DbSession

from app.integrations.openf1.client import OpenF1Client
from app.models.session import Session as SessionModel
from ingestion.services import (
    entries,
    intervals,
    laps,
    meetings,
    pit_stops,
    positions,
    race_control,
    seasons,
    session_results,
    sessions,
    stints,
    weather,
)

logger = logging.getLogger(__name__)


def ingest_session_data(client: OpenF1Client, db: DbSession, session: SessionModel) -> dict[str, int]:
    """Ingests every per-session data type for an already-existing session row."""
    counts: dict[str, int] = {}

    driver_id_by_number = entries.ingest_entries(client, db, session.session_key, session.id)
    counts["entries"] = len(driver_id_by_number)
    db.commit()

    steps = [
        ("laps", lambda: laps.ingest_laps(client, db, session.session_key, session.id, driver_id_by_number)),
        (
            "positions",
            lambda: positions.ingest_positions(client, db, session.session_key, session.id, driver_id_by_number),
        ),
        (
            "pit_stops",
            lambda: pit_stops.ingest_pit_stops(client, db, session.session_key, session.id, driver_id_by_number),
        ),
        (
            "intervals",
            lambda: intervals.ingest_intervals(client, db, session.session_key, session.id, driver_id_by_number),
        ),
        ("stints", lambda: stints.ingest_stints(client, db, session.session_key, session.id, driver_id_by_number)),
        ("weather", lambda: weather.ingest_weather(client, db, session.session_key, session.id)),
        (
            "race_control",
            lambda: race_control.ingest_race_control(
                client, db, session.session_key, session.id, driver_id_by_number
            ),
        ),
        (
            "session_results",
            lambda: session_results.ingest_session_results(
                client, db, session.session_key, session.id, driver_id_by_number
            ),
        ),
    ]

    for name, step in steps:
        try:
            counts[name] = step()
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Session %s: failed to ingest %s - continuing", session.session_key, name)
            counts[name] = 0

    return counts


def ingest_session(client: OpenF1Client, db: DbSession, session_key: int) -> dict[str, int]:
    session = sessions.ensure_session(client, db, session_key)
    db.commit()
    return ingest_session_data(client, db, session)


def ingest_meeting(client: OpenF1Client, db: DbSession, meeting_key: int) -> dict[int, dict[str, int]]:
    meeting = meetings.ensure_meeting(client, db, meeting_key)
    db.commit()

    results: dict[int, dict[str, int]] = {}
    for record, _raw in client.get_sessions(meeting_key=meeting.meeting_key):
        try:
            session = sessions.upsert_session_from_record(db, meeting.id, record)
            db.commit()
            results[session.session_key] = ingest_session_data(client, db, session)
        except Exception:
            db.rollback()
            logger.exception("Meeting %s: failed to ingest session %s - continuing", meeting_key, record.session_key)
            results[record.session_key] = {}
    return results


def ingest_season(client: OpenF1Client, db: DbSession, year: int) -> dict[int, dict[int, dict[str, int]]]:
    seasons.upsert_season(db, year)
    db.commit()

    results: dict[int, dict[int, dict[str, int]]] = {}
    for record, _raw in client.get_meetings(year=year):
        try:
            meeting = meetings.upsert_meeting_from_record(db, record)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Season %s: failed to ingest meeting %s - continuing", year, record.meeting_key)
            continue

        meeting_results: dict[int, dict[str, int]] = {}
        for session_record, _raw2 in client.get_sessions(meeting_key=meeting.meeting_key):
            try:
                session = sessions.upsert_session_from_record(db, meeting.id, session_record)
                db.commit()
                meeting_results[session.session_key] = ingest_session_data(client, db, session)
            except Exception:
                db.rollback()
                logger.exception(
                    "Season %s: failed to ingest session %s in meeting %s - continuing",
                    year,
                    session_record.session_key,
                    meeting.meeting_key,
                )
                meeting_results[session_record.session_key] = {}
        results[meeting.meeting_key] = meeting_results

    return results
